import time
import json
import subprocess
from neo4j import GraphDatabase

# Neo4j Configuration
NEO4J_URI = "bolt://localhost:7687"  # Update if needed
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"  # Replace with your actual password

# Kafka Configuration
KAFKA_CONTAINER = "kafka"  # Kafka container name
TOPIC = "users-topic"

# Neo4j Connection
class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def fetch_users_with_connections(self):
        """Retrieve users and their adjacency list from Neo4j."""
        query = """
        MATCH (u:User)
        OPTIONAL MATCH (u)-[r]->(other:User)
        RETURN u.userID AS userID, u.name AS name, 
               u.email AS email, collect({relationship: type(r), userID: other.userID, name: other.name}) AS connections
        """
        with self.driver.session() as session:
            result = session.run(query)
            users = []
            for record in result:
                # Remove None values (for users with no connections)
                connections = [conn for conn in record["connections"] if conn["userID"] is not None]
                users.append({
                    "userID": record["userID"],
                    "name": record["name"],
                    "email": record["email"],
                    "connections": connections
                })
            return users

def publish_users_to_kafka():
    """Fetch users from Neo4j and publish in batches of 5 every 20 seconds using Kafka CLI."""
    neo4j_conn = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    users = neo4j_conn.fetch_users_with_connections()
    neo4j_conn.close()

    batch_size = 5

    for i in range(0, len(users), batch_size):
        batch = users[i:i + batch_size]

        for user in batch:
            # Convert to JSON string
            message = json.dumps(user)

            # Use subprocess to call Kafka CLI
            command = f"echo '{message}' | docker exec -i {KAFKA_CONTAINER} kafka-console-producer --broker-list localhost:9092 --topic {TOPIC}"
            subprocess.run(command, shell=True, check=True)
            
            print(f"Published via CLI: {message}")

        print(f"Batch {i//batch_size + 1} sent.")
        time.sleep(20)  # Wait 20 seconds before sending the next batch

if __name__ == "__main__":
    publish_users_to_kafka()
