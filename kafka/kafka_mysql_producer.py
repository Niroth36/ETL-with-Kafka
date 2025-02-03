import time
import json
import mysql.connector
from kafka import KafkaProducer
from decimal import Decimal

# MySQL Connection
mysql_config = {
    "host": "localhost",  # Change to the actual MySQL container host if needed
    "port": 3307,         # The mapped port of MySQL in docker-compose
    "user": "cl_user",
    "password": "cluserpassword",
    "database": "cl_shop"
}

# Kafka Configuration
KAFKA_BROKER = "localhost:9092"  # Adjust if Kafka runs on another host
TOPIC = "clothes-topic"

# Connect to Kafka
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def fetch_clothes():
    """Fetch all clothes from MySQL database."""
    try:
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clothes")
        clothes = cursor.fetchall()
        
        # Convert Decimal price to float for JSON serialization
        for cloth in clothes:
            cloth["price"] = float(cloth["price"])  # Convert Decimal to float
        
        cursor.close()
        connection.close()
        return clothes
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []

def publish_to_kafka():
    """Fetch clothes and publish them to Kafka in batches of 10 every 10 seconds."""
    clothes = fetch_clothes()
    batch_size = 10

    for i in range(0, len(clothes), batch_size):
        batch = clothes[i:i + batch_size]
        for cloth in batch:
            producer.send(TOPIC, cloth)
            print(f"Published: {cloth}")

        producer.flush()
        print(f"Batch {i//batch_size + 1} sent.")
        time.sleep(10)  # Wait for 10 seconds before publishing next batch

if __name__ == "__main__":
    publish_to_kafka()
