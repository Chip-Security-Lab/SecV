from neo4j import GraphDatabase
from typing import Dict, List
import time
import traceback
from tqdm import tqdm

class Neo4jHandler:
    def __init__(self, uri: str, username: str, password: str):
        self.uri = uri
        self.user = username
        self.password = password
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.relationship_mapping = {
            "member of": "MEMBER_OF",
            "memberof": "MEMBER_OF",
            "peer of": "PEER_OF",
            "peerof": "PEER_OF",
            "child of": "CHILD_OF",
            "childof": "CHILD_OF",
            "parent of": "PARENT_OF",
            "parentof": "PARENT_OF",
            "has": "HAS",
            "hasmember": "HAS_MEMBER",
            "has member": "HAS_MEMBER",
            "potential resolved by": "POTENTIAL_RESOLVED_BY"
        }

    def close(self):
        self.driver.close()
        
    def normalize_relationship_type(self, rel_type: str) -> str:
        
        if not rel_type:
            return ""

        rel_type_lower = rel_type.lower().strip()

        if rel_type_lower in self.relationship_mapping:
            return self.relationship_mapping[rel_type_lower]
 
        if rel_type.isupper() and "_" in rel_type:
            return rel_type

        return rel_type.upper().replace(" ", "_")    
    def create_constraints(self):

        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:CWE) REQUIRE c.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Example) REQUIRE e.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (m:Mitigation) REQUIRE m.id IS UNIQUE")

    def create_entities(self, entities_data):

        if isinstance(entities_data, dict):
            if "entities" in entities_data:
                entities_data = entities_data["entities"]
                
            total_entities = sum(len(entities) for entities in entities_data.values() if isinstance(entities, dict))
            with tqdm(total=total_entities, desc="Creating Entities", leave=False) as pbar:
                for entity_type, entities in entities_data.items():
                    if isinstance(entities, dict):
                        for entity_id, attributes in entities.items():
                            try:
                                sanitized_attributes = self._sanitize_attributes(attributes)
                                with self.driver.session() as session:
                                    session.execute_write(
                                        self._create_entity_tx,
                                        entity_type,
                                        entity_id,
                                        sanitized_attributes
                                    )
                                pbar.update(1)
                            except Exception as e:
                                print(f"\n❌ Entity Creation Failed: {str(e)}")
                                self._reconnect()

    def _sanitize_attributes(self, attributes: Dict) -> Dict:

        sanitized = {}
        for k, v in attributes.items():
            if v is None:
                continue

            if isinstance(v, str) and k in sanitized:
                if len(v) > len(sanitized[k]):
                    sanitized[k] = v
            else:

                if isinstance(v, (str, int, float, bool, list)):
                    sanitized[k] = v
                else:
                    sanitized[k] = str(v)
                    
        return sanitized

    def _create_entity_tx(self, tx, entity_type: str, entity_id: str, attributes: Dict):


        query = (
            f"MERGE (n:{entity_type} {{id: $id}}) "
            "SET n += $properties "
            "RETURN n"
        )
        return tx.run(query, id=entity_id, properties=attributes)

    def _reconnect(self):

        try:
            if self.driver:
                self.driver.close()
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        except Exception as e:
            print(f"Reconnection failed: {str(e)}")

    def validate_relationship(self, relationship: Dict) -> bool:

        if not isinstance(relationship, dict):
            return False
            
        required_fields = ["source", "relationship", "target"]
        return all(field in relationship and relationship[field] for field in required_fields)

    def create_relationships(self, relationships_data):

        print("\n=== Starting Relationship Creation ===")
        
        if not relationships_data:
            print("Warning: No relationship data to create")
            return

        if isinstance(relationships_data, dict) and "relationships" in relationships_data:
            relationships_data = relationships_data["relationships"]
            
        with tqdm(relationships_data, desc="Creating Relationships") as pbar:
            for relationship in pbar:
                try:
                    if not self.validate_relationship(relationship):
                        print(f"\nWarning: Relationship validation failed: {relationship}")
                        continue
                    
                    relationship['relationship'] = self.normalize_relationship_type(relationship['relationship'])
                    pbar.set_description(f"waiting for creating")
                    
                    with self.driver.session() as session:
                        try:
                            result = session.execute_write(
                                self._create_relationship_tx,
                                relationship['source'],
                                relationship['relationship'],
                                relationship['target'],
                                relationship.get('properties', {})
                            )
                        except Exception as e:
                            if "SessionExpired" in str(e):
                                self._reconnect()
                                result = session.execute_write(
                                    self._create_relationship_tx,
                                    relationship['source'],
                                    relationship['relationship'],
                                    relationship['target'],
                                    relationship.get('properties', {})
                                )
                            else:
                                raise e
                            
                except Exception as e:
                    print(f"\nFailed to create relationship: {str(e)}")
                    traceback.print_exc()

    def _create_relationship_tx(self, tx, source_id: str, relationship_type: str, target_id: str, properties: Dict = None):

        if properties is None:
            properties = {}

        query = (
            f"MATCH (source) WHERE source.id = $source_id "
            f"MATCH (target) WHERE target.id = $target_id "
            f"MERGE (source)-[r:{relationship_type}]->(target) "
            f"SET r += $properties "
            f"RETURN type(r)"
        )
        
        return tx.run(
            query,
            source_id=source_id,
            target_id=target_id,
            properties=properties
        )

