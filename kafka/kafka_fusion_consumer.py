from kafka import KafkaConsumer
import json
from pymongo import MongoClient

# Kafka Configuration
KAFKA_BROKER = "localhost:9092"
TOPICS = ["clothes-topic", "users-topic"]

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "clothing_users"
MONGO_COLLECTION = "fused_data"

# Connect to MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB]
collection = db[MONGO_COLLECTION]

# Create Kafka Consumer
consumer = KafkaConsumer(
    *TOPICS,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    auto_offset_reset="earliest"
)

# In-memory data store for fusion
clothes_data = {}  # Stores clothes info indexed by clothID
users_data = {}  # Stores users indexed by userID

print("Listening for messages from Kafka...")

for message in consumer:
    data = message.value
    topic = message.topic

    if topic == "clothes-topic":
        # Store clothes data indexed by clothID
        clothID = data["clothID"]
        clothes_data[clothID] = data

    elif topic == "users-topic":
        # Store users data indexed by userID
        userID = data["userID"]
        users_data[userID] = data

    # Attempt to fuse data
    fused_entries = []
    for user_id, user_info in users_data.items():
        for connection in user_info["connections"]:
            # Ensure we have a matching clothing entry
            clothID = connection.get("userID")  # Using userID as reference to purchasedClothes
            if clothID and clothID in clothes_data:
                fused_entry = {
                    "userID": user_info["userID"],
                    "userName": user_info["name"],
                    "email": user_info["email"],
                    "connections": user_info["connections"],
                    "purchasedClothes": [
                        clothes_data[cid] for cid in user_info.get("purchasedClothes", []) if cid in clothes_data
                    ]
                }
                fused_entries.append(fused_entry)

    # Store in MongoDB
    if fused_entries:
        collection.insert_many(fused_entries)
        print(f"Stored {len(fused_entries)} fused records in MongoDB.")

