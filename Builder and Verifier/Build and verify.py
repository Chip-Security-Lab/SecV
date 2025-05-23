import os
from typing import List, Dict
import numpy as np
from rank_bm25 import BM25Okapi
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
import time
import math
import backoff
import requests.exceptions
from neo4j_handler import Neo4jHandler
from triplet_parser import TripletParser
import json
import traceback
import re

class CustomOpenAIEmbeddings:
    def __init__(self, api_key: str, base_url: str = None, model: str = "text-embedding-ada-002", timeout: int = 60):
        self.query = ""
        self.client = OpenAI(api_key=api_key, base_url=base_url if base_url else "https://api.openai.com/v1", timeout=timeout)
        self.model = model
        self.timeout = timeout

    @backoff.on_exception(backoff.expo, (requests.exceptions.RequestException, TimeoutError), max_tries=5)
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            batch_size = 100
            embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = self.client.embeddings.create(model=self.model, input=batch)
                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)
                time.sleep(0.5)
            return embeddings
        except Exception as e:
            print(f"Error in embed_documents: {str(e)}")
            raise

    @backoff.on_exception(backoff.expo, (requests.exceptions.RequestException, TimeoutError), max_tries=5)
    def embed_query(self, text: str) -> List[float]:
        try:
            response = self.client.embeddings.create(model=self.model, input=text)
            return response.data[0].embedding
        except Exception as e:
            print(f"Error in embed_query: {str(e)}")
            raise
# gpt-verifier
class verifier:
    def __init__(self, api_key: str, base_url: str = None, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key, base_url=base_url if base_url else "https://api.openai.com/v1")
        self.model = model
        
    @backoff.on_exception(backoff.expo, (requests.exceptions.RequestException, TimeoutError), max_tries=5)
    def chat(self, content: str) -> str:
        try:
            system_prompt = """As a CWE (Common Weakness Enumeration) verification expert, your primary goal is to ACCEPT responses unless they are catastrophically wrong. Assume all responses are correct by default.

            Verification Philosophy:
            - Start with the assumption that the response is CORRECT
            - Only look for catastrophic errors that make the information dangerously misleading
            - When in doubt, ALWAYS return "correct"
            - Accept different interpretations and perspectives

            Only Check For:
            1. Catastrophic Errors:
               - Completely wrong CWE category (e.g., describing a network vulnerability as a hardware issue)
               - Relationships that would cause dangerous misunderstandings
               - Examples/mitigations that could cause security incidents if followed

            Explicitly Ignore:
            - ALL formatting issues
            - ALL wording variations
            - ALL minor technical imprecisions
            - ALL partial or incomplete information
            - ALL subjective interpretations
            - ALL relationship nuances
            - ALL non-critical omissions

            Return Rules:
            - Return "correct" by default
            - Return "error" ONLY if the response could lead to dangerous security practices
            - If unsure, ALWAYS return "correct"

            CRITICAL: Your role is to ACCEPT responses whenever possible. If you can imagine any reasonable interpretation that makes the response valid, return "correct"."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Verify this response:\n\n{content}"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                max_tokens=5000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Verification error: {str(e)}")
            raise
    
class autoprompt:
    def __init__(self, api_key: str, base_url: str = None, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key, base_url=base_url if base_url else "https://api.openai.com/v1")
        self.model = model
        
    @backoff.on_exception(backoff.expo, (requests.exceptions.RequestException, TimeoutError), max_tries=5)
    def get_llm_response(self, prompt: str) -> str:
        try:
            system_prompt = """You are a helpful assistant."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=5000,
                presence_penalty=0.0,
                frequency_penalty=0.0
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error in getting LLM response: {str(e)}")
            raise

class HybridRetriever:
    def __init__(self, file_path: str, api_key: str, base_url: str = None, model: str = "text-embedding-ada-002", top_k: int = 5):
        try:
            self.top_k = top_k
            abs_file_path = os.path.abspath(file_path)
            if not os.path.exists(abs_file_path):
                raise FileNotFoundError(f"File not found: {abs_file_path}")
            with open(abs_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            if not content.strip():
                raise ValueError("File content is empty")
            raw_documents = [doc.strip() for doc in content.split("==================================================") if doc.strip()]
            if not raw_documents:
                raise ValueError("No documents found")
            self.documents = raw_documents
            # print(f"Total number of chunks: {len(self.documents)}")
            tokenized_docs = [doc.split() for doc in self.documents]
            self.bm25 = BM25Okapi(tokenized_docs)
            self.embeddings = CustomOpenAIEmbeddings(api_key=api_key, base_url=base_url, model=model)
            self.doc_embeddings = self.embeddings.embed_documents(self.documents)
        except Exception as e:
            print(f"Error during initialization: {str(e)}")
            raise

    def bm25_search(self, query: str, k: int = 5) -> List[Dict]:
        try:
            tokenized_query = query.split()
            scores = self.bm25.get_scores(tokenized_query)
            top_k_indices = np.argsort(scores)[-k:][::-1]
            results = []
            for i, idx in enumerate(top_k_indices, 1):
                results.append({"content": self.documents[idx], "score": float(scores[idx]), "rank": i})
            return results
        except Exception as e:
            print(f"Error in BM25 search: {e}")
            return []

    def vector_search(self, query: str, k: int = 5) -> List[Dict]:
        try:
            query_embedding = self.embeddings.embed_query(query)
            similarities = [self.cosine_similarity(query_embedding, doc_emb) for doc_emb in self.doc_embeddings]
            top_k_indices = np.argsort(similarities)[-k:][::-1]
            results = []
            for i, idx in enumerate(top_k_indices, 1):
                results.append({"content": self.documents[idx], "score": float(similarities[idx]), "rank": i})
            return results
        except Exception as e:
            print(f"Error in vector search: {e}")
            return []

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return float(dot_product / (norm1 * norm2))
        except Exception as e:
            print(f"Error in cosine similarity calculation: {e}")
            return 0.0

    def hybrid_search(self, query: str) -> List[Dict]:
        try:

            bm25_scores = self.bm25.get_scores(query.split())
            query_embedding = self.embeddings.embed_query(query)
            vector_scores = [self.cosine_similarity(query_embedding, doc_emb) for doc_emb in self.doc_embeddings]
            
            cwe_match = re.search(r'CWE-\d+', query)
            if cwe_match:
                target_cwe = cwe_match.group()

                for i, doc in enumerate(self.documents):
                    if target_cwe in doc:

                        bm25_scores[i] += max(bm25_scores) * 2.0  
                        vector_scores[i] += (1 - vector_scores[i]) * 0.8  
                        

                        doc_first_line = doc.split('\n')[0] if '\n' in doc else doc
                        if target_cwe in doc_first_line:

                            bm25_scores[i] *= 3.0 
                            vector_scores[i] = min(1.0, vector_scores[i] * 1.5)  
            
            final_results = self.simple_rrf_fusion(bm25_scores, vector_scores, query)  
            return final_results[:self.top_k]  
            
        except Exception as e:
            print(f"Error in hybrid search: {e}")
            return []

    def simple_rrf_fusion(self, bm25_scores: List[float], vector_scores: List[float], query: str, k: int = 60) -> List[Dict]:
        try:

            norm_bm25 = [(score - min(bm25_scores)) / (max(bm25_scores) - min(bm25_scores)) if max(bm25_scores) != min(bm25_scores) else 0.0 for score in bm25_scores]
            norm_vector = [(score - min(vector_scores)) / (max(vector_scores) - min(vector_scores)) if max(vector_scores) != min(vector_scores) else 0.0 for score in vector_scores]
            
            bm25_ranks = (-np.array(norm_bm25)).argsort().argsort() + 1
            vector_ranks = (-np.array(norm_vector)).argsort().argsort() + 1
            
            rrf_scores = []
            cwe_match = re.search(r'CWE-(\d+)', query)
            
            for i in range(len(self.documents)):

                rrf_bm25 = 1 / (k + bm25_ranks[i])
                rrf_vector = 1 / (k + vector_ranks[i])

                exact_match_score = 0.0
                if cwe_match:
                    target_cwe = cwe_match.group()
                    doc_lines = self.documents[i].split('\n')
                    for line in doc_lines[:4]:
                        if line.startswith('CWE:') and target_cwe in line:
                            exact_match_score = 1.0
                            break
                

                final_score = (
                    0.6 * exact_match_score +  
                    0.2 * norm_bm25[i] +       
                    0.15 * norm_vector[i] +     
                    0.05 * (rrf_bm25 + rrf_vector)  
                )
                
                rrf_scores.append((i, final_score))
            
            sorted_results = sorted(rrf_scores, key=lambda x: x[1], reverse=True)
            return [{"content": self.documents[idx], "score": round(score, 4)} for idx, score in sorted_results[:self.top_k]]
            
        except Exception as e:
            print(f"Error in RRF fusion: {e}")
            return []
class Analysts:
    def __init__(self, api_key: str, base_url: str = None, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key, base_url=base_url if base_url else "https://api.openai.com/v1")
        self.model = model
        
    @backoff.on_exception(backoff.expo, (requests.exceptions.RequestException, TimeoutError), max_tries=5)
    def get_llm_response(self, context: str, query: str) -> str:
        try:
            system_prompt = system_prompt = """You are an expert in cybersecurity and vulnerability analysis, specializing in CWE (Common Weakness Enumeration). 
Your task is to thoroughly analyze the given context and extract ALL vulnerability-related information and relationships.
Focus on:
1. Identifying ALL CWE entities mentioned in the text (including those in relationships sections)
2. Capturing ALL relationships between CWEs (memberof, childof, peerof)
3. Extracting examples and mitigations with their complete details
4. Ensuring no relationships or entities are missed"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nQuery:\n{query}"}
            ]
            
            # print("Sending request to OpenAI...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=5000,
                presence_penalty=0.0,
                frequency_penalty=0.0
            )
            # print("Response received successfully")
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error in getting LLM response: {str(e)}")
            print(f"Context preview: {context[:200]}...")
            raise
def get_cweprompt():
    return '''  
                ---
                I'd like you to crossover and mutate the following two prompts to generate a more effective one（But don't lose the details in prompt2):
                **Prompt 1**:
                Let's think step by step.

                ---

                **Prompt 2**:
                Analyze the given text to extract entities, attributes, and relationships following these steps:
                1. Entity Extraction (marked as -NODES-):
                Extract the following types of entities and their attributes:

                A. CWE Entities
                Attributes:
                - Abstraction
                - Description
                - Extended Description
                - Common Consequences
                - Weakness ID

                B. Example Entities
                Attributes:
                - Description (including example code and explanations)

                C. Mitigation Entities
                Attributes:
                - Phases
                - Description
                - Effectiveness

                2. Relationship Extraction (marked as -RELATIONSHIPS-):
                Extract relationships between entities using the format: (entity1, relationship_type, entity2)

                Relationship types:
                - Between CWEs: peerof, memberof, childof
                - CWE -> Example: has
                - CWE -> Mitigation: potential resolved by

                Required Output Format:
                ############
                -NODES-
                [Entity1 Name]
                [Entity1's attributes]

                [Entity2 Name]
                [Entity2's attributes]
                ...

                -RELATIONSHIPS-
                (entity1, relationship_type, entity2)
                (entity3, relationship_type, entity4)
                ...
                ############

                Important Notes:
                1. Entity names must be complete and accurate
                2. Attribute values should preserve the original text content
                3. Relationships must follow defined directions and types
                4. Only extract explicitly stated entities and relationships, no inference

                Here's an example of the expected output format:
                -----------------------------------------------------
                -chunk-
                ==================================================
                CWE:
                CWE-1245: Improper Finite State Machines (FSMs) in Hardware Logic

                Weakness ID:
                1245

                Abstraction:
                Base

                Description:
                Faulty finite state machines (FSMs) in the hardware logic allow an attacker to put the system in an undefined state, to cause a denial of service (DoS) or gain privileges on the victim's system.

                Extended Description:
                The functionality and security of the system heavily depend on the implementation of FSMs. FSMs can be used to indicate the current security state of the system. Lots of secure data operations and data transfers rely on the state reported by the FSM. Faulty FSM designs that do not account for all states, either through undefined states (left as don't cares) or through incorrect implementation, might lead an attacker to drive the system into an unstable state from which the system cannot recover without a reset, thus causing a DoS. Depending on what the FSM is used for, an attacker might also gain additional privileges to launch further attacks and compromise the security guarantees.

                Common Consequences:
                
                Scope	Impact	Likelihood
                Availability
                Access Control	
                Technical Impact: Unexpected State; DoS: Crash, Exit, or Restart; DoS: Instability; Gain Privileges or Assume Identity

                Potential Mitigations:
                Phases: Architecture and Design; Implementation

                Define all possible states and handle all unused states through default statements. Ensure that system defaults to a secure state.
                Effectiveness: High

                Relationships:
                
                + Relevant to the view "Hardware Design" (CWE-1194)
                Nature	Type	ID	Name
                MemberOf	Category	1199	General Circuit and Logic Design Concerns

                Demonstrative Examples:
                Example 1

                The Finite State Machine (FSM) shown in the "bad" code snippet below assigns the output ("out") based on the value of state, which is determined based on the user provided input ("user_input").

                (bad code)
                Example Language: Verilog 
                module fsm_1(out, user_input, clk, rst_n);
                input [2:0] user_input;
                input clk, rst_n;
                output reg [2:0] out;
                reg [1:0] state;
                always @ (posedge clk or negedge rst_n )
                begin
                if (!rst_n)
                state = 3'h0;
                else
                case (user_input)
                3'h0:
                3'h1:
                3'h2:
                3'h3: state = 2'h3;
                3'h4: state = 2'h2;
                3'h5: state = 2'h1;
                endcase
                end
                out <= {1'h1, state};
                endmodule

                The case statement does not include a default to handle the scenario when the user provides inputs of 3'h6 and 3'h7. Those inputs push the system to an undefined state and might cause a crash (denial of service) or any other unanticipated outcome.

                Adding a default statement to handle undefined inputs mitigates this issue. This is shown in the "Good" code snippet below. The default statement is in bold.

                (good code)
                Example Language: Verilog 
                case (user_input)
                3'h0:
                3'h1:
                3'h2:
                3'h3: state = 2'h3;
                3'h4: state = 2'h2;
                3'h5: state = 2'h1;
                default: state = 2'h0;
                endcase

                ==================================================

                -result-
                ############
                -NODES-
                NODE1:
                CWE-1245: Improper Finite State Machines (FSMs) in Hardware Logic
                NODE1's attribute：
                Abstraction:Base
                Description:Faulty finite state machines (FSMs) in the hardware logic allow an attacker to put the system in an undefined state, to cause a denial of service (DoS) or gain privileges on the victim's system.
                Extended Description:The functionality and security of the system heavily depend on the implementation of FSMs. FSMs can be used to indicate the current security state of the system. Lots of secure data operations and data transfers rely on the state reported by the FSM. Faulty FSM designs that do not account for all states, either through undefined states (left as don't cares) or through incorrect implementation, might lead an attacker to drive the system into an unstable state from which the system cannot recover without a reset, thus causing a DoS. Depending on what the FSM is used for, an attacker might also gain additional privileges to launch further attacks and compromise the security guarantees.

                NODE2:CWE-1245 Mitigation1
                NODE2's attribute
                Phases: Architecture and Design; Implementation
                Description:Define all possible states and handle all unused states through default statements. Ensure that system 
                Effectiveness: High
                NODE3:CWE-1245 Example 1
                NODE3's attribute
                description:
                The Finite State Machine (FSM) shown in the "bad" code snippet below assigns the output ("out") based on the value of state, which is determined based on the user provided input ("user_input").

                (bad code)
                Example Language: Verilog 
                module fsm_1(out, user_input, clk, rst_n);
                input [2:0] user_input;
                input clk, rst_n;
                output reg [2:0] out;
                reg [1:0] state;
                always @ (posedge clk or negedge rst_n )
                begin
                if (!rst_n)
                state = 3'h0;
                else
                case (user_input)
                3'h0:
                3'h1:
                3'h2:
                3'h3: state = 2'h3;
                3'h4: state = 2'h2;
                3'h5: state = 2'h1;
                endcase
                end
                out <= {1'h1, state};
                endmodule

                The case statement does not include a default to handle the scenario when the user provides inputs of 3'h6 and 3'h7. Those inputs push the system to an undefined state and might cause a crash (denial of service) or any other unanticipated outcome.

                Adding a default statement to handle undefined inputs mitigates this issue. This is shown in the "Good" code snippet below. The default statement is in bold.

                (good code)
                Example Language: Verilog 
                case (user_input)
                3'h0:
                3'h1:
                3'h2:
                3'h3: state = 2'h3;
                3'h4: state = 2'h2;
                3'h5: state = 2'h1;
                default: state = 2'h0;
                endcase

                NODE4:CWE-1199:General Circuit and Logic Design Concerns
                NODE4's attribute:None
                ############
                Relationships
                (CWE-1245: Improper Finite State Machines (FSMs) in Hardware Logic,member of,CWE-1199:General Circuit and Logic Design Concerns)
                (CWE-1245: Improper Finite State Machines (FSMs) in Hardware Logic,has,CWE-1245 Example 1)
                (CWE-1245: Improper Finite State Machines (FSMs) in Hardware Logic,potential resolved by,CWE-1245 Mitigation1)
                -----------------------------------------------

                Please analyze the provided text and generate output following this exact format.
                ---
                Finally, select and return only the most effective prompt content (don't have anything else like title etc.) that best guides the extraction and structuring of triplets from the text according to the given instructions.
                ---
                '''

def get_extraction_prompt():
    return '''
Analyze the given text to extract entities, attributes, and relationships following these steps:

1. Entity Extraction (marked as -NODES-):
Extract the following types of entities and their attributes:

A. CWE Entities
Attributes:
- Abstraction
- Description
- Extended Description
- Common Consequences
- Weakness ID

B. Example Entities
Attributes:
- Description (including example code and explanations)

C. Mitigation Entities
Attributes:
- Phases
- Description
- Effectiveness

2. Relationship Extraction (marked as -RELATIONSHIPS-):
Extract relationships between entities using the format: (entity1, relationship_type, entity2)

Relationship types:
- Between CWEs: peerof, memberof, childof
- CWE -> Example: has
- CWE -> Mitigation: potential resolved by

Required Output Format:
############
-NODES-
[Entity1 Name]
[Entity1's attributes]

[Entity2 Name]
[Entity2's attributes]
...

-RELATIONSHIPS-
(entity1, relationship_type, entity2)
(entity3, relationship_type, entity4)
...
############

Important Notes:
1. Entity names must be complete and accurate
2. Attribute values should preserve the original text content
3. Relationships must follow defined directions and types
4. Only extract explicitly stated entities and relationships, no inference

Here's an example of the expected output format:
-----------------------------------------------------
-chunk-
==================================================
CWE:
CWE-1245: Improper Finite State Machines (FSMs) in Hardware Logic

Weakness ID:
1245

Abstraction:
Base

Description:
Faulty finite state machines (FSMs) in the hardware logic allow an attacker to put the system in an undefined state, to cause a denial of service (DoS) or gain privileges on the victim's system.

Extended Description:
The functionality and security of the system heavily depend on the implementation of FSMs. FSMs can be used to indicate the current security state of the system. Lots of secure data operations and data transfers rely on the state reported by the FSM. Faulty FSM designs that do not account for all states, either through undefined states (left as don't cares) or through incorrect implementation, might lead an attacker to drive the system into an unstable state from which the system cannot recover without a reset, thus causing a DoS. Depending on what the FSM is used for, an attacker might also gain additional privileges to launch further attacks and compromise the security guarantees.

Common Consequences:
 
Scope	Impact	Likelihood
Availability
Access Control	
Technical Impact: Unexpected State; DoS: Crash, Exit, or Restart; DoS: Instability; Gain Privileges or Assume Identity

Potential Mitigations:
Phases: Architecture and Design; Implementation

Define all possible states and handle all unused states through default statements. Ensure that system defaults to a secure state.
Effectiveness: High

Relationships:
 
+ Relevant to the view "Hardware Design" (CWE-1194)
Nature	Type	ID	Name
MemberOf	Category	1199	General Circuit and Logic Design Concerns

Demonstrative Examples:
Example 1

The Finite State Machine (FSM) shown in the "bad" code snippet below assigns the output ("out") based on the value of state, which is determined based on the user provided input ("user_input").

(bad code)
Example Language: Verilog 
module fsm_1(out, user_input, clk, rst_n);
input [2:0] user_input;
input clk, rst_n;
output reg [2:0] out;
reg [1:0] state;
always @ (posedge clk or negedge rst_n )
begin
if (!rst_n)
state = 3'h0;
else
case (user_input)
3'h0:
3'h1:
3'h2:
3'h3: state = 2'h3;
3'h4: state = 2'h2;
3'h5: state = 2'h1;
endcase
end
out <= {1'h1, state};
endmodule

The case statement does not include a default to handle the scenario when the user provides inputs of 3'h6 and 3'h7. Those inputs push the system to an undefined state and might cause a crash (denial of service) or any other unanticipated outcome.

Adding a default statement to handle undefined inputs mitigates this issue. This is shown in the "Good" code snippet below. The default statement is in bold.

(good code)
Example Language: Verilog 
case (user_input)
3'h0:
3'h1:
3'h2:
3'h3: state = 2'h3;
3'h4: state = 2'h2;
3'h5: state = 2'h1;
default: state = 2'h0;
endcase

==================================================

-result-
############
-NODES-
NODE1:
CWE-1245: Improper Finite State Machines (FSMs) in Hardware Logic
NODE1's attribute：
Abstraction:Base
Description:Faulty finite state machines (FSMs) in the hardware logic allow an attacker to put the system in an undefined state, to cause a denial of service (DoS) or gain privileges on the victim's system.
Extended Description:The functionality and security of the system heavily depend on the implementation of FSMs. FSMs can be used to indicate the current security state of the system. Lots of secure data operations and data transfers rely on the state reported by the FSM. Faulty FSM designs that do not account for all states, either through undefined states (left as don't cares) or through incorrect implementation, might lead an attacker to drive the system into an unstable state from which the system cannot recover without a reset, thus causing a DoS. Depending on what the FSM is used for, an attacker might also gain additional privileges to launch further attacks and compromise the security guarantees.

NODE2:CWE-1245 Mitigation1
NODE2's attribute
Phases: Architecture and Design; Implementation
Description:Define all possible states and handle all unused states through default statements. Ensure that system 
Effectiveness: High
NODE3:CWE-1245 Example 1
NODE3's attribute
description:
The Finite State Machine (FSM) shown in the "bad" code snippet below assigns the output ("out") based on the value of state, which is determined based on the user provided input ("user_input").

(bad code)
Example Language: Verilog 
module fsm_1(out, user_input, clk, rst_n);
input [2:0] user_input;
input clk, rst_n;
output reg [2:0] out;
reg [1:0] state;
always @ (posedge clk or negedge rst_n )
begin
if (!rst_n)
state = 3'h0;
else
case (user_input)
3'h0:
3'h1:
3'h2:
3'h3: state = 2'h3;
3'h4: state = 2'h2;
3'h5: state = 2'h1;
endcase
end
out <= {1'h1, state};
endmodule

The case statement does not include a default to handle the scenario when the user provides inputs of 3'h6 and 3'h7. Those inputs push the system to an undefined state and might cause a crash (denial of service) or any other unanticipated outcome.

Adding a default statement to handle undefined inputs mitigates this issue. This is shown in the "Good" code snippet below. The default statement is in bold.

(good code)
Example Language: Verilog 
case (user_input)
3'h0:
3'h1:
3'h2:
3'h3: state = 2'h3;
3'h4: state = 2'h2;
3'h5: state = 2'h1;
default: state = 2'h0;
endcase

NODE4:CWE-1199:General Circuit and Logic Design Concerns
NODE4's attribute:None
############
Relationships
(CWE-1245: Improper Finite State Machines (FSMs) in Hardware Logic,member of,CWE-1199:General Circuit and Logic Design Concerns)
(CWE-1245: Improper Finite State Machines (FSMs) in Hardware Logic,has,CWE-1245 Example 1)
(CWE-1245: Improper Finite State Machines (FSMs) in Hardware Logic,potential resolved by,CWE-1245 Mitigation1)
-----------------------------------------------

Please analyze the provided text and generate output following this exact format.
'''

def main():
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_API_BASE")
        embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
        chat_model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
        top_k = int(os.getenv('TOP_K', '1'))
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "cwe.txt")
        id_copy_path = os.path.join(current_dir, "id.txt")

        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        if not neo4j_password:
            raise ValueError("Neo4j password not found in environment variables")       

        try:
            with open(id_copy_path, 'r') as f:
                cwe_ids = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            print(f"no file error: {id_copy_path}")
            cwe_ids = []
            

        queries = [f"what is {cwe_id}?" for cwe_id in cwe_ids]

        # print(queries)
        

        retriever = HybridRetriever(file_path=file_path, api_key=api_key, base_url=base_url, 
                                  model=embedding_model, top_k=top_k)
        anas = Analysts(api_key=api_key, base_url=base_url, model=chat_model)
        verifier1=verifier(api_key=api_key, base_url=base_url, model=chat_model)
        # Adaptprompt=get_cweprompt()
        # cwepromptor=autoprompt(api_key=api_key, base_url=base_url, model="gpt-4o-2024-11-20")
        # cweprompt=cwepromptor.get_llm_response(Adaptprompt)
        # print(cweprompt)
        # try:
        #     with open('adaptedprompt.txt', 'w', encoding='utf-8') as f:
        #         f.write(adaptedprompt.txt)
        #     print("success")
        # except Exception as e:
        #     print(f"error: {str(e)}")

        with open('adaptedprompt.txt', 'r', encoding='utf-8') as f:
            extraction_prompt = f.read()

        neo4j_handler = Neo4jHandler(neo4j_uri, neo4j_user, neo4j_password)
        triplet_parser = TripletParser(llm_client=OpenAI(api_key=api_key, base_url=base_url))
        

        # output_dir = os.path.join(current_dir, "parsed_results")
        # os.makedirs(output_dir, exist_ok=True)
        

        # all_entities = {"entities": {"CWE": {}, "Mitigation": {}, "Example": {}}}
        # all_relationships = {"relationships": []}
        
        # for query in queries:
        #     try:
        #         cwe_id = None
        #         match = re.search(r'CWE-\d+', query)
        #         if match:
        #             cwe_id = match.group()
        #         else:
        #             print(f"error")
        #             continue

        #         print(f"\n=== waiting: {cwe_id} ===")
                
                
        #         results = retriever.hybrid_search(query)
        #         if results:
        #             context = "\n".join([result['content'] for result in results])
        #             # print(context)
        #             try:
        #                 extraction_prompt = get_extraction_prompt()

        #                 llm_response = anas.get_llm_response(context, extraction_prompt)
                        
        #                 # while True:
        #                 #     llm_response = anas.get_llm_response(context, extraction_prompt)
        #                 #     verify_result = verifier1.chat(llm_response)
        #                 #     print("In verification..")
        #                 #     if verify_result.strip().lower() == "correct":
        #                 #         break
        #                 #     print("verify error and try again")

                        
        #                 print("verify success")
        #                 parsed_data = triplet_parser.parse_llm_response(llm_response)

        #                 print(json.dumps(parsed_data["entities"], indent=2, ensure_ascii=False))
        #                 print(json.dumps(parsed_data["relationships"], indent=2, ensure_ascii=False))

        #                 for entity_type in parsed_data["entities"]:
        #                     all_entities["entities"][entity_type].update(
        #                         parsed_data["entities"][entity_type]
        #                     )
 
        #                 all_relationships["relationships"].extend(
        #                     parsed_data["relationships"]
        #                 )
                        
        #                 # print(f"\n✅ ")
                        
        #             except Exception as e:
        #                 print(f"❌")
        #                 traceback.print_exc()
                
        #     except Exception as e:
        #         print(f"error: {str(e)}")
        #         traceback.print_exc()

        
        # entities_file = os.path.join(output_dir, "entities.json")
        # relationships_file = os.path.join(output_dir, "relationships.json")
        
        # with open(entities_file, 'w', encoding='utf-8') as f:
        #     json.dump(all_entities, f, indent=2, ensure_ascii=False)
        # print(f"✅ entities file: {entities_file}")
        
        # with open(relationships_file, 'w', encoding='utf-8') as f:
        #     json.dump(all_relationships, f, indent=2, ensure_ascii=False)
        # print(f"✅ relationships file: {relationships_file}")

        print("\n=== wait for Neo4j data processing ===")
        try:
            entities_path = os.path.join("parsed_results", "entities.json")
            relationships_path = os.path.join("parsed_results", "relationships.json")
            
            with open(entities_path, 'r', encoding='utf-8') as f:
                entities_data = json.load(f)
            with open(relationships_path, 'r', encoding='utf-8') as f:
                relationships_data = json.load(f)
                
            neo4j_handler.create_constraints()
            neo4j_handler.create_entities(entities_data)
            neo4j_handler.create_relationships(relationships_data)
            print("\n✅ Neo4j data processing completed")
        except Exception as e:
            print(f"\n❌ Neo4j error: {str(e)}")
            traceback.print_exc()

        
    except Exception as e:
        print(f"process error: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()

# $env:NEO4J_URI = "Your URI"
# $env:NEO4J_USER = "Neo4j"
# $env:NEO4J_PASSWORD = "Your password"
# $env:OPENAI_API_KEY = "Your API_KEY" 
# $env:OPENAI_API_BASE = "if you need" 


# Processing results have been saved in the parsed_results folder.
# You can store it directly to your neo4j repository.