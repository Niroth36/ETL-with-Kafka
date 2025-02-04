import time
import json
import mysql.connector
import subprocess
from decimal import Decimal

# MySQL Connection
mysql_config = {
    "host": "localhost",  # Change if needed
    "port": 3307,         # Mapped port for MySQL in docker-compose
    "user": "cl_user",
    "password": "cluserpassword",
    "database": "cl_shop"
}

# Kafka Configuration
KAFKA_CONTAINER = "kafka"  # Kafka container name
TOPIC = "clothes-topic"

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
    """Fetch clothes and publish them to Kafka using CLI in batches of 10 every 10 seconds."""
    clothes = fetch_clothes()
    batch_size = 10

    for i in range(0, len(clothes), batch_size):
        batch = clothes[i:i + batch_size]
        for cloth in batch:
            # Convert to JSON string
            message = json.dumps(cloth)

            # Use subprocess to call Kafka CLI
            command = f"echo '{message}' | docker exec -i {KAFKA_CONTAINER} kafka-console-producer --broker-list localhost:9092 --topic {TOPIC}"
            subprocess.run(command, shell=True, check=True)
            
            print(f"Published via CLI: {message}")

        print(f"Batch {i//batch_size + 1} sent.")
        time.sleep(10)  # Wait 10 seconds before sending next batch

if __name__ == "__main__":
    publish_to_kafka()
