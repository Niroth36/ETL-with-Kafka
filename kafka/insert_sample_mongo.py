from pymongo import MongoClient

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "clothing_users"
MONGO_COLLECTION = "fused_data"

# Sample Data
sample_data = {
  "userID": 1,
  "userName": "Alice",
  "email": "alice@example.com",
  "connections": [
    {"relationship": "FRIEND", "userID": 2, "name": "Bob"},
    {"relationship": "PARTNER", "userID": 3, "name": "Charlie"}
  ],
  "purchasedClothes": [
    {"clothID": 1, "style": "athletic", "color": "Red", "price": 49.99, "brand": "Nike"},
    {"clothID": 2, "style": "casual", "color": "Blue", "price": 39.99, "brand": "Levis"}
  ]
}

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

# Insert Data
insert_result = collection.insert_one(sample_data)

print(f"Inserted document ID: {insert_result.inserted_id}")
