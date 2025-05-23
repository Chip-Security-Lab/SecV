EXTRACTION_PROMPT = """
Please analyze the provided CWE information and extract ALL components following this exact format:

1. Entity Extraction (-NODES-):
Extract ALL entities, including:
- Primary CWE entity
- ALL related CWE entities mentioned (including those in relationship sections)
- ALL examples
- ALL mitigations

Required attributes:
For CWE entities:
- Weakness ID
- Description
- Extended Description (if available)

For Examples:
- Full description including code snippets

For Mitigations:
- Phase
- Description
- Effectiveness

2. Relationship Extraction (-RELATIONSHIPS-):
Extract ALL relationships using format: (entity1, relationship_type, entity2)
Include:
- ALL CWE-to-CWE relationships (memberof, childof, peerof)
- ALL CWE-to-Example relationships (has)
- ALL CWE-to-Mitigation relationships (potential resolved by)

Important:
- Extract ALL CWEs mentioned in any section, including Relationships
- Preserve exact relationship types as shown in the text
- Don't miss any entities or relationships

Example Output Format:
############
-NODES-
NODE1:CWE-1245: Improper Finite State Machines (FSMs) in Hardware Logic
NODE1's attribute：
Abstraction:Base
Description:Faulty finite state machines (FSMs) in the hardware logic...
Extended Description:The functionality and security of the system...

NODE2:CWE-1245 Mitigation1
NODE2's attribute
Phases: Architecture and Design; Implementation
Description:Define all possible states...
Effectiveness: High

NODE3:CWE-1245 Example 1
NODE3's attribute
description:[Full example with code]

NODE4:CWE-1199:General Circuit and Logic Design Concerns
NODE4's attribute:None
############
Relationships
(CWE-1245: Improper Finite State Machines (FSMs) in Hardware Logic,member of,CWE-1199:General Circuit and Logic Design Concerns)
(CWE-1245: Improper Finite State Machines (FSMs) in Hardware Logic,has,CWE-1245 Example 1)
(CWE-1245: Improper Finite State Machines (FSMs) in Hardware Logic,potential resolved by,CWE-1245 Mitigation1)
############

Please analyze the provided text and generate output following this exact format.
"""
