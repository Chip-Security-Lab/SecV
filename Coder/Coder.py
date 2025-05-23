from langchain_community.chat_models import ChatOpenAI  
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import OpenAI  
from langchain.chains import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)
import numpy as np
import re
import string
from neo4j import GraphDatabase, basic_auth
import pandas as pd
from collections import deque
import itertools
from typing import Dict, List
import pickle
import json
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize 
import openai
from sentence_transformers import SentenceTransformer
import os
import csv
from rank_bm25 import BM25Okapi
from sklearn.metrics.pairwise import cosine_similarity
import sys
import warnings
from time import sleep
import backoff
import requests
from openai import OpenAI
import pandas as pd
import pyverilog
from pyverilog.vparser.parser import parse
import pyverilog.vparser.parser as parser
import os
import csv
import tempfile
import subprocess
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
# from llama_cpp import Llama

def codestral(query):
    prompt = f"""
    Please act as a professional Verilog designer.

    {query}
    ---
    # Output format #
    Please give me the complete verilog code(as string with proper formatting, including appropriate newlines and indentation, don't using any Markdown or code block syntax.) for the implementation module Follow this format:

    module example(
    input wire clk,
    input wire rst_n
    );
    // Implementation
    endmodule

    Do not include any explanations, markdown formatting, or additional text. Start directly with the module declaration and end with endmodule.
    ---
    """

    client = OpenAI(
    base_url = "https://integrate.api.nvidia.com/v1",
    api_key = "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"
    )

    completion = client.chat.completions.create(
    model="mistralai/mamba-codestral-7b-v0.1",
    messages=[{"role":"user","content":prompt}],
    temperature=0.9,
    top_p=1,
    max_tokens=1024,
    stream=True
    )
    result = ""
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            result += chunk.choices[0].delta.content
    return result





def codestral_kg(answer_kg: str, query: str):
    prompt = f"""
    Please act as a professional Verilog designer.

    {query}
    ---
    There are secure advice and examples that you must understand and follow.
    {answer_kg}
    ---
    # Output format #
    Please give me the complete verilog code(as string with proper formatting, including appropriate newlines and indentation, don't using any Markdown or code block syntax.) for the implementation module Follow this format:

    module example(
    input wire clk,
    input wire rst_n
    );
    // Implementation
    endmodule

    Do not include any explanations, markdown formatting, or additional text. Start directly with the module declaration and end with endmodule.
    ---
    """
    client = OpenAI(
    base_url = "https://integrate.api.nvidia.com/v1",
    api_key = "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"
    )

    completion = client.chat.completions.create(
    model="mistralai/mamba-codestral-7b-v0.1",
    messages=[{"role":"user","content":prompt}],
    temperature=0.9,
    top_p=1,
    max_tokens=1024,
    stream=True
    )

    result = ""
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            result += chunk.choices[0].delta.content
    return result     

def llama3(query):

    prompt = f"""
    Please act as a professional Verilog designer.

    {query}
    ---
    # Output format #
    Please give me the complete verilog code(as string with proper formatting, including appropriate newlines and indentation, don't using any Markdown or code block syntax.) for the implementation module Follow this format:

    module example(
    input wire clk,
    input wire rst_n
    );
    // Implementation
    endmodule

    Do not include any explanations, markdown formatting, or additional text. Start directly with the module declaration and end with endmodule.
    ---
    """

    client = OpenAI(
        base_url = "https://integrate.api.nvidia.com/v1",
        api_key = "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"
    )
    completion = client.chat.completions.create(
        model="meta/llama-3.3-70b-instruct",
        messages=[{"role":"user","content":prompt}],
        temperature=0.7,
        top_p=0.9,
        max_tokens=1024,
        stream=True
    )
    result = ""
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            result+=chunk.choices[0].delta.content
            
    return result

def llama3_kg(answer_kg: str, query: str):

    prompt = f"""
    Please act as a professional Verilog designer.

    {query}
    ---
    There are secure advice and examples that you must understand and follow.
    {answer_kg}
    ---
    # Output format #
    Please give me the complete verilog code(as string with proper formatting, including appropriate newlines and indentation, don't using any Markdown or code block syntax.) for the implementation module Follow this format:

    module example(
    input wire clk,
    input wire rst_n
    );
    // Implementation
    endmodule

    Do not include any explanations, markdown formatting, or additional text. Start directly with the module declaration and end with endmodule.
    ---
    """

    client = OpenAI(
        base_url = "https://integrate.api.nvidia.com/v1",
        api_key = "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"
    )
    completion = client.chat.completions.create(
        model="meta/llama-3.3-70b-instruct",
        messages=[{"role":"user","content":prompt}],
        temperature=0.7,
        top_p=0.9,
        max_tokens=1024,
        stream=True
    )
    result = ""
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            result += chunk.choices[0].delta.content
    
    return result

def chat_35(prompt, api_key: str, base_url: str = None):
    client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url if base_url else "https://api.openai.com/v1"
    )
    
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Please act as a professional Verilog designer."},
            {"role": "user", "content": prompt + """
---
# Output format #
Please give me the complete verilog code(as string with proper formatting, including appropriate newlines and indentation, don't using any Markdown or code block syntax.) for the implementation module Follow this format:

module example(
input wire clk,
input wire rst_n
);
// Implementation
endmodule

Do not include any explanations, markdown formatting, or additional text. Start directly with the module declaration and end with endmodule.
---
"""}
        ]
    )
    return completion.choices[0].message.content

def chat_4(prompt, api_key: str, base_url: str = None):
    client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url if base_url else "https://api.openai.com/v1"
    )
    
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Please act as a professional Verilog designer."},
            {"role": "user", "content": prompt + """
---
# Output format #
Please give me the complete verilog code(as string with proper formatting, including appropriate newlines and indentation, don't using any Markdown or code block syntax.) for the implementation module Follow this format:

module example(
input wire clk,
input wire rst_n
);
// Implementation
endmodule

Do not include any explanations, markdown formatting, or additional text. Start directly with the module declaration and end with endmodule.
---
"""}
        ]
    )
    return completion.choices[0].message.content

def final_answer_35(answer_kg: str, decision_tree: str, query: str, api_key: str, base_url: str = None):
    chat35 = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0.8,
        openai_api_key=api_key,
        openai_api_base=base_url if base_url else "https://api.openai.com/v1"
    )
    
    messages = [
        SystemMessage(content=f"""
---
Please act as a professional Verilog designer.
{query}
---
There are secure advice and examples that you must understand and follow.
{answer_kg}
---
# Output format #
Please give me the complete verilog code(as string with proper formatting, including appropriate newlines and indentation, don't using any Markdown or code block syntax.) for the implementation module Follow this format:

module example(
input wire clk,
input wire rst_n
);
// Implementation
endmodule

Do not include any explanations, markdown formatting, or additional text. Start directly with the module declaration and end with endmodule.
---
""")
    ]
    
    result = chat35(messages)
    return result.content

def final_answer_4(answer_kg: str, decision_tree: str, query: str, api_key: str, base_url: str = None):
    chat4 = ChatOpenAI(
        model_name="gpt-4",
        temperature=0.7,
        openai_api_key=api_key,
        openai_api_base=base_url if base_url else "https://api.openai.com/v1"
    )
    
    messages = [
        SystemMessage(content=f"""
---
Please act as a professional Verilog designer.
{query}
---
There are secure advice and examples that you must understand and follow.
{answer_kg}
---
# Output format #
Please give me the complete verilog code(as string with proper formatting, including appropriate newlines and indentation, don't using any Markdown or code block syntax.) for the implementation module Follow this format:

module example(
input wire clk,
input wire rst_n
);
// Implementation
endmodule

Do not include any explanations, markdown formatting, or additional text. Start directly with the module declaration and end with endmodule.
---
""")
    ]
    
    result = chat4(messages)
    return result.content

def get_entity_neighbors(entity_name: str, k: int) -> List[dict]:

    query = f"""
    MATCH (e:CWE)-[r*1..{k}]-(n)
    WHERE e.name = $entity_name
    AND ANY(label IN labels(n) WHERE label IN ['Example', 'Mitigation'])
    RETURN e.id as source, 
           [rel in r | type(rel)] as relationship_types,
           n.id as target,
           properties(n) as neighbor_props,
           labels(n) as neighbor_labels
    """
    
    try:
        result = session.run(query, entity_name=entity_name)
        neighbor_list = []
        
        for record in result:
            neighbor_info = {
                'source': record["source"],
                'relationships': record["relationship_types"],
                'target': record["target"],
                'properties': dict(record["neighbor_props"]),
                'labels': record["neighbor_labels"]
            }
            neighbor_list.append(neighbor_info)
        
        return neighbor_list
        
    except Exception as e:
        print(f"Error querying neighbors for entity {entity_name}: {e}")
        return []


def cosine_similarity_manual(x, y):
    dot_product = np.dot(x, y.T)
    norm_x = np.linalg.norm(x, axis=-1)
    norm_y = np.linalg.norm(y, axis=-1)
    sim = dot_product / (norm_x[:, np.newaxis] * norm_y)
    return sim


def prompt_document(question,instruction):
    template = """
    You are an excellent AI doctor, and you can diagnose diseases and recommend medications based on the symptoms in the conversation.\n\n
    Patient input:\n
    {question}
    \n\n
    You have some medical knowledge information in the following:
    {instruction}
    \n\n
    What disease does the patient have? What tests should patient take to confirm the diagnosis? What recommened medications can cure the disease?
    """

    prompt = PromptTemplate(
        template = template,
        input_variables = ["question","instruction"]
    )

    system_message_prompt = SystemMessagePromptTemplate(prompt = prompt)
    system_message_prompt.format(question = question,
                                 instruction = instruction)

    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt,human_message_prompt])
    chat_prompt_with_values = chat_prompt.format_prompt(question = question,\
                                                        instruction = instruction,\
                                                        text={})

    response_document_bm25 = chat(chat_prompt_with_values.to_messages()).content

    return response_document_bm25

def generate_and_save_entity_embeddings():
    query = """
    MATCH (e:CWE)  
    RETURN e.name as entity_name
    """
    with driver.session() as session:
        result = session.run(query)
        entities = [record["entity_name"] for record in result]


    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Generating embeddings...")
    embeddings = model.encode(entities, 
                            batch_size=32,  
                            show_progress_bar=True,
                            normalize_embeddings=True)  
    
    # 4. 保存实体和对应的嵌入向量
    entity_data = {
        "entities": entities,
        "embeddings": embeddings.tolist()  
    }
    save_path = os.path.join('cwedata', 'entity_embeddings.json')
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(entity_data, f, ensure_ascii=False, indent=2)

    return entities, embeddings

def generate_and_save_clue_embeddings():

    with open('cwedata/querys.json', 'r', encoding='utf-8') as f:
        queries_data = json.load(f)
    
    model = SentenceTransformer('all-MiniLM-L6-v2')

    embedded_queries = []
    
    for query in queries_data['queries']:

        clue_embeddings = model.encode(query['clue'], 
                                     batch_size=32,
                                     show_progress_bar=True,
                                     normalize_embeddings=True)

        embedded_query = {
            'description': query['design_description'],
            'clues': [
                {
                    'text': clue,
                    'embedding': embedding.tolist()  
                }
                for clue, embedding in zip(query['clue'], clue_embeddings)
            ]
        }
        embedded_queries.append(embedded_query)

    save_path = os.path.join('cwedata', 'cluesembedded.json')
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump({'embedded_queries': embedded_queries}, f, ensure_ascii=False, indent=2)
    
    print(f"Clue embeddings saved to {save_path}")
    print(f"Processed {len(embedded_queries)} queries")
    return embedded_queries

class SecurityEvaluator:
    def __init__(self, api_key: str, base_url: str = None, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key, base_url=base_url if base_url else "https://api.openai.com/v1")
        self.model = model
        
    @backoff.on_exception(backoff.expo, (requests.exceptions.RequestException, TimeoutError), max_tries=5)
    def evaluate(self, content: str, source_entity: str) -> bool:
        try:
            print("\n=== Evaluation Input ===")
            print(f"Source Entity: {source_entity}")
            print("Content:")
            print(content)
            print("=====================")
            
            system_prompt = """As a security information evaluator, your goal is to be LENIENT in accepting security-related content. Start with the assumption that the information is sufficient unless clearly lacking.

            Evaluation Philosophy:
            - Start with the assumption that the information is SUFFICIENT
            - Look for ANY security-related content (Mitigation or Example)
            - When in doubt, return "yes"
            - Accept different types of security information
            
            Consider Sufficient If:
            - Has ANY Mitigation information
            - Has ANY Example information
            - Has ANY security-related properties
            - Has ANY meaningful security context
            
            Explicitly Ignore:
            - Quality of the information
            - Completeness of the information
            - Number of nodes (even one good node is enough)
            - Format of the information
            
            Return Rules:
            - Return ONLY "yes" or "no"
            - Default to "yes" if unsure
            - Return "no" ONLY if absolutely no security content exists
            
            CRITICAL: Your role is to ACCEPT information whenever possible. If you can find ANY security-related content, return "yes"."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""Please evaluate if there are ANY security information about {source_entity}.

Neighbor information:
{content}"""}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=5
            )
            
            answer = response.choices[0].message.content.strip().lower()
            print("\n=== Evaluation Result ===")
            print(f"Answer: {answer}")
            print("=====================\n")
            
            return answer == "yes"
            
        except Exception as e:
            print(f"Evaluation error: {str(e)}")
            return False

class SecurityKnowledgeProcessor:
    def __init__(self, api_key: str, base_url: str = None, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key, base_url=base_url if base_url else "https://api.openai.com/v1")
        self.model = model
        
    @backoff.on_exception(backoff.expo, (requests.exceptions.RequestException, TimeoutError), max_tries=5)
    def process(self, content: str) -> str:

        try:
            system_prompt = """You are a security expert. Extract and format the security information from the provided text.

IMPORTANT: Start your response directly with the format below, no introduction text.

Extraction Rules:
1. For Mitigations:
   - Extract the number from 'CWE-XXXX Mitigation X' in the id field
   - Use only the 'description' content
   - Format as 'advice X.[description]'

2. For Examples:
   - Look for content between '(good code)' and the next section
   - Include 'Example Language: XXX' if present
   - Keep exact code formatting
   - Remove any duplicate language specifications

Format the output exactly as:
--
Secure advice：
--
##
advice 1.[Mitigation 1 description only]
##

##
advice 2.[Mitigation 2 description only]
##
--
Secure Examples：
--
##
Example1：
(Good Code)
[Language specification if any]
[Good code content only]
##

##
Example2：
(Good Code)
[Language specification if any]
[Good code content only]
##
Here is a example:
-untreated content-
  Properties: {'id': 'CWE-1262 Mitigation 2', 'Phases': 'Implementation', 'description': 'Ensure that access control policies for register access are implemented in accordance with the specified design.', 'Effectiveness': 'Not specified'}

  Properties: {'id': 'CWE-1262 Mitigation 1', 'Phases': 'Architecture and Design', 'description': 'Design proper policies for hardware register access from software.', 'Effectiveness': 'Not specified'}

  Properties: {'id': 'CWE-1262 Example 2', 'description': "The example code is taken from the Control/Status Register (CSR) module inside the processor core of the HACK@DAC'19 buggy CVA6 SoC. In RISC-V ISA, the CSR file contains different sets of registers with different privilege levels, e.g., user mode (U), supervisor mode (S), hypervisor mode (H), machine mode (M), and debug mode (D), with different read-write policies, read-only (RO) and read-write (RW). For example, machine mode, which is the highest privilege mode in a RISC-V system, registers should not be accessible in user, supervisor, or hypervisor modes.\n(bad code)\nExample Language: Verilog \nif (csr_we || csr_read) begin\nif ((riscv::priv_lvl_t'(priv_lvl_o & csr_addr.csr_decode.priv_lvl) != csr_addr.csr_decode.priv_lvl) && !(csr_addr.address==riscv::CSR_MEPC)) begin\ncsr_exception_o.cause = riscv::ILLEGAL_INSTR;\ncsr_exception_o.valid = 1'b1;\nend\n// check access to debug mode only CSRs\nif (csr_addr_i[11:4] == 8'h7b && !debug_mode_q) begin\ncsr_exception_o.cause = riscv::ILLEGAL_INSTR;\ncsr_exception_o.valid = 1'b1;\nend\nend\nThe vulnerable example code allows the machine exception program counter (MEPC) register to be accessed from a user mode program by excluding the MEPC from the access control check. MEPC as per the RISC-V specification can be only written or read by machine mode code. Thus, the attacker in the user mode can run code in machine mode privilege (privilege escalation).\nTo mitigate the issue, fix the privilege check so that it throws an Illegal Instruction Exception for user mode accesses to the MEPC register.\n(good code)\nExample Language: Verilog \nif (csr_we || csr_read) begin\nif ((riscv::priv_lvl_t'(priv_lvl_o & csr_addr.csr_decode.priv_lvl) != csr_addr.csr_decode.priv_lvl)) begin\ncsr_exception_o.cause = riscv::ILLEGAL_INSTR;\ncsr_exception_o.valid = 1'b1;\nend\n// check access to debug mode only CSRs\nif (csr_addr_i[11:4] == 8'h7b && !debug_mode_q) begin\ncsr_exception_o.cause = riscv::ILLEGAL_INSTR;\ncsr_exception_o.valid = 1'b1;\nend\nend"}

  Properties: {'id': 'CWE-1262 Example 1', 'description': 'The register interface provides software access to hardware functionality. This functionality is an attack surface. This attack surface may be used to run untrusted code on the system through the register interface. As an example, cryptographic accelerators require a mechanism for software to select modes of operation and to provide plaintext or ciphertext data to be encrypted or decrypted as well as other functions. This functionality is commonly provided through registers.\n(bad code)\nCryptographic key material stored in registers inside the cryptographic accelerator can be accessed by software.\n(good code)\nKey material stored in registers should never be accessible to software. Even if software can provide a key, all read-back paths to software should be disabled.'}
-extraction result-
--
Secure advice：
--
##
advice 1.Design proper policies for hardware register access from software.
##

##
advice 2.Ensure that access control policies for register access are implemented in accordance with the specified design.
##
--
Secure Examples：
--
##
Example1：
(Good Code)
Key material stored in registers should never be accessible to software.
Even if software can provide a key, all read-back paths to software should be disabled.
##

##
Example2:
-
(Good Code)
Example Language: Verilog
Language: Verilog

if (csr_we || csr_read) begin
    // Check privilege level for the CSR access
    if ((riscv::priv_lvl_t'(priv_lvl_o & csr_addr.csr_decode.priv_lvl) != csr_addr.csr_decode.priv_lvl)) begin
        csr_exception_o.cause = riscv::ILLEGAL_INSTR;
        csr_exception_o.valid = 1'b1;
    end

    // Check access to debug mode only CSRs
    if (csr_addr_i[11:4] == 8'h7b && !debug_mode_q) begin
        csr_exception_o.cause = riscv::ILLEGAL_INSTR;
        csr_exception_o.valid = 1'b1;
    end
end
##

"""       
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please format the following security information:\n\n{content}"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=4096
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Processing error: {str(e)}")
            raise


class DecisionTreeGenerator:
    def __init__(self, api_key: str, base_url: str = None, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key, base_url=base_url if base_url else "https://api.openai.com/v1")
        self.model = model
        
    @backoff.on_exception(backoff.expo, (requests.exceptions.RequestException, TimeoutError), max_tries=5)
    def generate(self, path: str, answer_kg: str) -> str:
        try:
            system_prompt = """Generate ONLY the decision tree ASCII diagram. Do not add any additional text.

1. Path Structure Analysis:
- Analyze paths like: CWE-1262 --[POTENTIAL_RESOLVED_BY]--> CWE-1262 Mitigation 1
- Identify parent nodes, relationships, and child nodes
- Identify leaf nodes that will contain final results

2. Hierarchical Structure:
- Maintain strict alternation: relationship → entity → relationship → entity
- Every relationship and entity must show its Evidence source
- Mark all leaf nodes with (result)(Evidence X)
- Use exact Evidence numbers from the input paths

3. Node Expansion Rules:
For Mitigation nodes:
- Add APPLIES_DURING
  * phase
  * HAS_DESCRIPTION
    └── description (result)(Evidence X)
- Add DESCRIBED_BY
  * description
  * CONNECTED_TO
    └── details (result)(Evidence X)

For Example nodes:
- Add EXEMPLIFIES
  * description
  * HAS_CODE
    * code
    * INCLUDES
      ├── snippet1: bad practice (result)(Evidence X)
      └── snippet2: good practice (result)(Evidence X)
- Add ILLUSTRATES
  └── scenario (result)(Evidence X)

4. Formatting Requirements:
- Use proper indentation
- Use correct tree symbols:
  * ├── for non-last items
  * └── for last items
  * │   for vertical lines
- Every node must show its Evidence source
- Every leaf node must be marked with (result)

Example Format:
CWE-1262
├── POTENTIAL_RESOLVED_BY (Evidence 1)
│   ├── CWE-1262 Mitigation 1 (Evidence 2)
│   │   ├── APPLIES_DURING
│   │   │   ├── phase
│   │   │   └── HAS_DESCRIPTION
│   │   │       └── description: Explanation of phase for Mitigation 1 (result)(Evidence 2)
│   │   └── DESCRIBED_BY
│   │       ├── description
│   │       └── CONNECTED_TO
│   │           └── Additional details for Mitigation 1 (result)(Evidence 2)
│   └── CWE-1262 Mitigation 2 (Evidence 1)
│       ├── APPLIES_DURING
│       │   ├── phase
│       │   └── HAS_DESCRIPTION
│       │       └── description: Explanation of phase for Mitigation 2 (result)(Evidence 1)
│       └── DESCRIBED_BY
│           ├── description
│           └── CONNECTED_TO
│               └── Additional details for Mitigation 2 (result)(Evidence 1)
└── HAS (Evidence 3)
    ├── CWE-1262 Example 1 (Evidence 4)
    │   ├── EXEMPLIFIES
    │   │   ├── description
    │   │   └── HAS_CODE
    │   │       ├── code
    │   │       └── INCLUDES
    │   │           ├── snippet1: Code showing bad practice (result)(Evidence 4)
    │   │           └── snippet2: Code showing good practice (result)(Evidence 4)
    │   └── ILLUSTRATES
    │       └── Detailed scenario for Example 1 (result)(Evidence 4)
    └── CWE-1262 Example 2 (Evidence 3)
        ├── EXEMPLIFIES
        │   ├── description
        │   └── HAS_CODE
        │       ├── code
        │       └── INCLUDES
        │           ├── snippet1: Code showing bad practice (result)(Evidence 3)
        │           └── snippet2: Code showing good practice (result)(Evidence 3)
        └── ILLUSTRATES
            └── Detailed scenario for Example 2 (result)(Evidence 3)
"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Indicates the path information to be processed:\n{path}\n\n"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=4096
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Tree generation error: {str(e)}")
            raise

def rtl_coder(current_description: str):

    torch.cuda.empty_cache()
    prompt = "Please act as a professional Verilog designer.\n"+current_description + """\n
---
# Output format #
Please give me the complete verilog code(as string with proper formatting, including appropriate newlines and indentation, don't using any Markdown or code block syntax.) for the implementation module Follow this format:

module example(
input wire clk,
input wire rst_n
);
// Implementation
endmodule

Do not include any explanations, markdown formatting, or additional text. Start directly with the module declaration and end with endmodule.
---
"""
    
    # Load model and tokenizer
    gpu_name = 0
    tokenizer = AutoTokenizer.from_pretrained("ishorn5/RTLCoder-Deepseek-v1.1")
    model = AutoModelForCausalLM.from_pretrained("ishorn5/RTLCoder-Deepseek-v1.1", torch_dtype=torch.float16, device_map=gpu_name)
    model.eval()
    
    # Sample
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(gpu_name)
    sample = model.generate(input_ids, max_new_tokens=1024, temperature=0.5, top_p=0.9)
    s_full = tokenizer.decode(sample[0])
    return s_full

def rtl_coder_kg(current_description: str, answer_kg: str, tree: str):

    torch.cuda.empty_cache()
    # 构建包含 KG 信息的 prompt
    prompt = f"""
---
Please act as a professional Verilog designer.
{current_description}
---
There are secure advice and examples that you must understand and follow.
{answer_kg}
---
# Output format #
Please give me the complete verilog code(as string with proper formatting, including appropriate newlines and indentation, don't using any Markdown or code block syntax.) for the implementation module Follow this format:

module example(
input wire clk,
input wire rst_n
);
// Implementation
endmodule

Do not include any explanations, markdown formatting, or additional text. Start directly with the module declaration and end with endmodule.
---
"""
    
    # Load model and tokenizer
    gpu_name = 0
    tokenizer = AutoTokenizer.from_pretrained("ishorn5/RTLCoder-Deepseek-v1.1")
    model = AutoModelForCausalLM.from_pretrained("ishorn5/RTLCoder-Deepseek-v1.1", torch_dtype=torch.float16, device_map=gpu_name)
    model.eval()
    
    # Sample
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(gpu_name)
    sample = model.generate(input_ids, max_new_tokens=1024, temperature=0.5, top_p=0.9)
    s_full = tokenizer.decode(sample[0])

    return s_full

if __name__ == "__main__":

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", message="Importing LLMs from langchain is deprecated")

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_API_BASE")
    

    evaluator = SecurityEvaluator(api_key=api_key, base_url=base_url, model="gpt-4o-mini")
    processor = SecurityKnowledgeProcessor(api_key=api_key, base_url=base_url,model="gpt-4o")
    tree_generator = DecisionTreeGenerator(api_key=api_key, base_url=base_url,model="gpt-4o-mini")

    chat = ChatOpenAI(
        openai_api_key=api_key,
        base_url=base_url,
    )



    # first step: generate embeddings
    # Neo4j数据库连接
    # uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    # username = os.getenv("NEO4J_USER", "neo4j")
    # password = os.getenv("NEO4J_PASSWORD")   
    
    # try:
    #     driver = GraphDatabase.driver(uri, auth=(username, password))
    #     session = driver.session()
    # except Exception as e:
    #     print(f"Failed to connect to Neo4j: {e}")
    #     raise
    # print("Loading entity embeddings...")
    # entities, embeddings = generate_and_save_entity_embeddings()
    # print("Loading clue embeddings...")
    # embedded_queries = generate_and_save_clue_embeddings()


    with open('cwedata/entity_embeddings.json', 'r', encoding='utf-8') as f:
        entity_data = json.load(f)
        entities = entity_data['entities']
        entity_embeddings = np.array(entity_data['embeddings'])
    

    with open('cwedata/cluesembedded.json', 'r', encoding='utf-8') as f:
        clue_data = json.load(f)

        print("waiting for the processing to complete...")

        for i, query in enumerate(clue_data['embedded_queries']):

            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            username = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD")   
            
            try:
                driver = GraphDatabase.driver(uri, auth=(username, password))
                session = driver.session()
            except Exception as e:
                print(f"Failed to connect to Neo4j: {e}")
                raise

            current_description = query['description']
            current_matches = []
            

            for clue_info in query['clues']:
                clue_text = clue_info['text']
                clue_embedding = np.array(clue_info['embedding'])
                

                similarities = np.dot(entity_embeddings, clue_embedding) / (
                    np.linalg.norm(entity_embeddings, axis=1) * np.linalg.norm(clue_embedding)
                )
                
                best_match_idx = np.argmax(similarities)
                matched_entity = entities[best_match_idx]
                
                
                # K = 1
                # while K < 5:
                #     print(f"\nTrying with K={K} hops...")
                #     neighbors = get_entity_neighbors(matched_entity, k=K)
                    
                #     if len(neighbors) > 0:
                #         print(f"Found {len(neighbors)} neighbors")
                        

                #         content = ""
                #         source_entity = neighbors[0]['source']
                #         for neighbor in neighbors:
                #             content += f"- {neighbor['source']} --[{neighbor['relationships']}]--> {neighbor['target']}\n"
                #             content += f"  Labels: {neighbor['labels']}\n"
                #             content += f"  Properties: {neighbor['properties']}\n\n"
                        
                #         if evaluator.evaluate(content, source_entity):
                #             print(f"✓ Found sufficient security information at K={K}")
                #             break
                #         else:
                #             print(f"✗ Security information not sufficient, trying K={K+1}...")
                #     else:
                #         print(f"No neighbors found at K={K}, trying next hop...")
                    
                #     K += 1

                path=""
                question_kg = ""
                count=1
                K = 1
                neighbors = get_entity_neighbors(matched_entity, k=K)
                best_match = {
                    'clue': clue_text,
                    'matched_entity': matched_entity,
                    'similarity': float(similarities[best_match_idx]),
                    'neighbors': neighbors
                }
                
                current_matches.append(best_match)
                
                
                # print(f"Clue: {clue_text}")
                # print(f"Matched Entity: {matched_entity}")
                # print(f"Similarity Score: {best_match['similarity']:.3f}")
                # print("\nNeighbors:")

                for neighbor in neighbors:
                        # answer_kg += f"- {neighbor['source']} --[{neighbor['relationships']}]--> {neighbor['target']}\n"
                        # answer_kg += f"  Labels: {neighbor['labels']}\n"
                        # answer_kg += f"  Properties: {neighbor['properties']}\n\n"
                        question_kg += f"  Properties: {neighbor['properties']}\n\n"
                        path += f"Evidence {count}: {neighbor['source']} --[{neighbor['relationships']}]--> {neighbor['target']}\n"
                        count += 1
                  
            # print(path)

            # print("answer_kg")
            answer_kg = processor.process(question_kg)
            # print(answer_kg)

            tree = tree_generator.generate(path, answer_kg)
            # print(tree)

            # print(current_description)


            os.makedirs('result', exist_ok=True)
            query_dir = f'result/query{i+1}'
            os.makedirs(query_dir, exist_ok=True)

            # # # Experiment : GPT 4 AND GPT 4 + KG
            # for j in range(5):
            #     os.makedirs('result', exist_ok=True)
            #     query_dir = f'result/query{i+1}'
            #     os.makedirs(query_dir, exist_ok=True)
                
            #     gpt4_dir = f'{query_dir}/gpt4'
            #     gpt4kg_dir = f'{query_dir}/gpt4_kg'
            #     os.makedirs(gpt4_dir, exist_ok=True)
            #     os.makedirs(gpt4kg_dir, exist_ok=True)
                
            #     result_4 = chat_4(current_description, api_key, base_url)
            #     with open(f'{gpt4_dir}/gen{j+1}.txt', 'w', encoding='utf-8') as f:
            #         f.write(result_4)
                
            #     result_4_kg = final_answer_4(
            #         answer_kg=answer_kg,
            #         decision_tree=tree,
            #         query=current_description,
            #         api_key=api_key,
            #         base_url=base_url
            #     )
            #     with open(f'{gpt4kg_dir}/gen{j+1}.txt', 'w', encoding='utf-8') as f:
            #         f.write(result_4_kg)

            # # #Experiment : Rtl coder
            # for j in range(5):
            #     rtl_dir = f'{query_dir}/rtl_coder'
            #     rtl_kg_dir = f'{query_dir}/rtl_coder_kg'
            #     os.makedirs(rtl_dir, exist_ok=True)
            #     os.makedirs(rtl_kg_dir, exist_ok=True)
                
            #     result_rtl = rtl_coder(current_description)
            #     with open(f'{rtl_dir}/gen{j+1}.txt', 'w', encoding='utf-8') as f:
            #         f.write(result_rtl)

            #     result_rtlcoder_kg = rtl_coder_kg(
            #         current_description=current_description,
            #         answer_kg=answer_kg,
            #         tree=tree
            #     )
            #     with open(f'{rtl_kg_dir}/gen{j+1}.txt', 'w', encoding='utf-8') as f:
            #         f.write(result_rtlcoder_kg)

            # Experiment : llama3
            # for j in range(5):
            #     llama3_dir = f'{query_dir}/llama3'
            #     llama3_kg_dir = f'{query_dir}/llama3_kg'
            #     os.makedirs(llama3_dir, exist_ok=True)
            #     os.makedirs(llama3_kg_dir, exist_ok=True)
            #     result_llama3 = llama3(current_description)
            #     with open(f'{llama3_dir}/gen{j+1}.txt', 'w', encoding='utf-8') as f:
            #         f.write(result_llama3)
            #     result_llama3_kg = llama3_kg(answer_kg=answer_kg, query=current_description)
            #     with open(f'{llama3_kg_dir}/gen{j+1}.txt', 'w', encoding='utf-8') as f:
            #         f.write(result_llama3_kg)

            print(f"Query {i+1}/{len(clue_data['embedded_queries'])} ✔")

            



        
                
               

               