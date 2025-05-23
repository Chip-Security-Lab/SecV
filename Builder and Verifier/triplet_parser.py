import re
import json
from typing import Dict, List, Set, Tuple
from openai import OpenAI
import os
import traceback

class TripletParser:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def parse_llm_response(self, response: str) -> Dict:
        print("=== Starting Parsing ===")
        try:
            if not self.llm_client:
                print("❌ Error: LLM client not initialized")
                

            
            parse_prompt = f"""

You are tasked with parsing the provided node and relationship information into a structured JSON format. There are three types of nodes: CWE nodes, Example nodes, and Mitigation nodes. Each type of node has specific attributes. Extract and include the appropriate details for each node based on its type:

provided node and relationship information:
{response}

### Node Types:
1. **CWE Nodes** (e.g., CWE-1245):
   - **id**: The CWE ID (e.g., "CWE-1245").
   - **name**: The name of the CWE, excluding the CWE ID prefix (e.g., "Improper Finite State Machines (FSMs) in Hardware Logic").
   - **description**: A brief description of the CWE (e.g., "Faulty FSMs in hardware logic can cause denial of service (DoS) or privilege escalation").
   - **abstraction**: The level of abstraction for the CWE (e.g., "Base").
   - **extended_description**: A more detailed explanation, including technical aspects, potential impacts, or specific scenarios (e.g., "The functionality and security of the system heavily depend on FSM implementations. Faulty FSMs can lead to instability and security risks...").

2. **Mitigation Nodes** (e.g., CWE-1245 Mitigation1):
   - **description**: A brief description of the mitigation (e.g., "Define all possible states and handle unused states through default statements").
   - **Phases**: The phases in which the mitigation should be applied (e.g., "Architecture and Design; Implementation").
   - **Effectiveness**: The effectiveness of the mitigation (e.g., "High").

3. **Example Nodes** (e.g., CWE-1245 Example 1):
   - **description**: A comprehensive description that includes the example's details, such as:
     - The **bad code** that demonstrates the issue.
     - The **good code** that mitigates the problem.
     - An **explanation** of why the bad code is problematic and how the good code resolves the issue.

### Relationship Information:
For each relationship between nodes, extract the following:
- **source**: The source node ID (e.g., "CWE-1245").
- **relationship**: The type of relationship (e.g., "member of", "has", "potential resolved by").
- **target**: The target node ID (e.g., "CWE-1199").
- **properties**: Any additional properties associated with the relationship (leave empty if not applicable).


### Your output should be structured in JSON format as shown below:

{{
    "entities": {{
        "CWE": {{
            "CWE-1245": {{
                "id": "CWE-1245",
                "name": "Improper Finite State Machines (FSMs) in Hardware Logic",
                "description": "Faulty finite state machines (FSMs) in hardware logic allow an attacker to put the system in an undefined state, causing denial of service (DoS) or privilege escalation.",
                "abstraction": "Base",
                "extended_description": "The functionality and security of the system heavily depend on FSM implementations. FSMs are used to indicate security states, and faulty FSMs might allow attackers to push the system into an unstable state that causes a DoS or compromise the system's security."
            }},
            "CWE-1199": {{
                "id": "CWE-1199",
                "name": "General Circuit and Logic Design Concerns",
                "description": null,
                "abstraction": null,
                "extended_description": null
            }}
        }},
        "Mitigation": {{
            "CWE-1245 Mitigation1": {{
                "description": "Define all possible states and handle unused states through default statements.",
                "Phases": "Architecture and Design; Implementation",
                "Effectiveness": "High"
            }}
        }},
        "Example": {{
            "CWE-1245 Example 1": {{
                "description": "The FSM shown in the 'bad' code snippet below has no default case to handle undefined inputs.\\n\\n(bad code)\\nExample Language: Verilog\\nmodule fsm_1(out, user_input, clk, rst_n);\\ninput [2:0] user_input;\\ninput clk, rst_n;\\noutput reg [2:0] out;\\nreg [1:0] state;\\nalways @ (posedge clk or negedge rst_n )\\nbegin\\nif (!rst_n)\\nstate = 3'h0;\\nelse\\ncase (user_input)\\n3'h0: state = 2'h3;\\n3'h1: state = 2'h2;\\n3'h2: state = 2'h1;\\n3'h3: state = 2'h0;\\nendcase\\nend\\nout <= {{1'h1, state}};\\nendmodule\\n\\nThe case statement does not include a default to handle the scenario when the user provides inputs of 3'h6 and 3'h7. Those inputs push the system to an undefined state and might cause a crash (denial of service) or any other unanticipated outcome.\\n\\nAdding a default statement to handle undefined inputs mitigates this issue. This is shown in the 'Good' code snippet below. The default statement is in bold.\\n\\n(good code)\\nExample Language: Verilog\\ncase (user_input)\\n3'h0: state = 2'h3;\\n3'h1: state = 2'h2;\\n3'h2: state = 2'h1;\\n3'h3: state = 2'h0;\\ndefault: state = 2'h0;\\nendcase"
            }}
        }}
    }},
    "relationships": [
        {{
            "source": "CWE-1245",
            "relationship": "member of",
            "target": "CWE-1199",
            "properties": {{}}
        }},
        {{
            "source": "CWE-1245",
            "relationship": "has",
            "target": "CWE-1245 Example 1",
            "properties": {{}}
        }},
        {{
            "source": "CWE-1245",
            "relationship": "potential resolved by",
            "target": "CWE-1245 Mitigation1",
            "properties": {{}}
        }}
    ]
}}"""

            # 修改系统提示，使其更严格
            system_prompt = """You are a specialized assistant for parsing CWE data into structured JSON format. 
Always use the actual CWE ID as the id field, not NODE labels.
You must ONLY return a valid JSON object with the exact structure shown in the example.
Do not include any explanatory text or markdown formatting."""

            # 最多重试4次
            max_retries = 4
            for attempt in range(max_retries):
                try:
                    print(f"🔄 process {attempt + 1}/{max_retries}")
                    
                    chat_response = self.llm_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": system_prompt
                            },
                            {
                                "role": "user", 
                                "content": parse_prompt
                            }
                        ],
                        temperature=0.1
                    )
                    
                    if chat_response and chat_response.choices:
                        content = chat_response.choices[0].message.content
                       
                        try:
                            parsed_data = json.loads(content)
                            if self._validate_json_structure(parsed_data):
                                print("✅ Data parsing success")
                                return parsed_data
                            else:
                                print(f"❌ JSON structure error (attempt {attempt + 1}/{max_retries})")
                                continue
                        except json.JSONDecodeError as json_err:
                            print(f"❌ JSON error (attempt {attempt + 1}/{max_retries}): {str(json_err)}")
                            continue
                except Exception as e:
                    print(f"❌ API error (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    continue
            
            
            print(f"❌ process {max_retries} times, but still failed")
            return {'entities': {}, 'relationships': []}
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            traceback.print_exc()
            return {'entities': {}, 'relationships': []}

    def _validate_json_structure(self, data: Dict) -> bool:
        """验证JSON结构是否符合预期格式"""
        try:
            # 检查顶层结构
            if not isinstance(data, dict):
                return False
            if not all(k in data for k in ['entities', 'relationships']):
                return False
            
            # 检查entities结构
            if not isinstance(data['entities'], dict):
                return False
            if not all(k in data['entities'] for k in ['CWE']):
                return False
            
            # 检查relationships结构
            if not isinstance(data['relationships'], list):
                return False
            for rel in data['relationships']:
                if not all(k in rel for k in ['source', 'relationship', 'target', 'properties']):
                    return False
                
            return True
        except Exception:
            return False