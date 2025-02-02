from time import sleep
import json
from kafka import KafkaProducer
from neo4j import GraphDatabase

# Kafka Configuration
KAFKA_TOPIC = "users-topic"
KAFKA_BROKER = "localhost:9092"

# Neo4j Connection
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    request_timeout_ms=5000,  # Set a timeout of 5 seconds
    retry_backoff_ms=500  # Retry in case of failure
)

def fetch_users():
    """Fetch 5 users from Neo4j along with their adjacency list."""
    query = """
    MATCH (u:User)
    OPTIONAL MATCH (u)-[r]->(connectedUser:User)
    RETURN u.userID AS userID, u.name AS name, u.email AS email, 
           COLLECT({relationship: TYPE(r), userID: connectedUser.userID, name: connectedUser.name}) AS connections
    LIMIT 5
    """
    with driver.session() as session:
        result = session.run(query)
        users = []
        for record in result:
            users.append({
                "userID": record["userID"],
                "name": record["name"],
                "email": record["email"],
                "connections": [conn for conn in record["connections"] if conn["userID"] is not None]
            })
    return users

def send_to_kafka():
    """Send users data to Kafka every 20 seconds."""
    while True:
        users = fetch_users()
        for user in users:
            producer.send(KAFKA_TOPIC, value=user)
            print(f"Sent: {user}")
        sleep(20)

if __name__ == "__main__":
    send_to_kafka()
