from time import sleep
import json
import mysql.connector
from kafka import KafkaProducer
from decimal import Decimal

# Kafka Configuration
KAFKA_TOPIC = "clothes-topic"
KAFKA_BROKER = "localhost:9092"  # Use "kafka:9092" if running inside Docker

# MySQL Connection
mysql_conn = mysql.connector.connect(
    host="localhost",  # Use "mysql-db" if running inside Docker
    port=3307,
    user="cl_user",
    password="cluserpassword",
    database="cl_shop"
)
mysql_cursor = mysql_conn.cursor(dictionary=True)

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    request_timeout_ms=5000,  # Set a timeout of 5 seconds
    retry_backoff_ms=500,  # Retry in case of failure
)

def fetch_clothes():
    """Fetch 10 clothes from MySQL and convert DECIMAL values to float."""
    mysql_cursor.execute("SELECT * FROM clothes LIMIT 10;")
    rows = mysql_cursor.fetchall()
    
    # Convert Decimal fields to float
    for row in rows:
        for key, value in row.items():
            if isinstance(value, Decimal):
                row[key] = float(value)
    
    return rows
    """Fetch 10 clothes from MySQL and convert DECIMAL values to float."""
    mysql_cursor.execute("SELECT * FROM clothes LIMIT 10;")
    rows = mysql_cursor.fetchall()
    
    # Convert Decimal fields to float
    for row in rows:
        for key, value in row.items():
            if isinstance(value, Decimal):
                row[key] = float(value)
    
    return rows

def send_to_kafka():
    """Send clothes data to Kafka every 10 seconds."""
    while True:
        clothes = fetch_clothes()
        for item in clothes:
            producer.send(KAFKA_TOPIC, value=item)
            print(f"Sent: {item}")
        sleep(10)

if __name__ == "__main__":
    send_to_kafka()
