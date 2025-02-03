from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "clothing_users"
MONGO_COLLECTION = "fused_data"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

@app.route('/get_purchased_products/<int:user_id>', methods=['GET'])
def get_purchased_products(user_id):
    """
    Retrieve the purchased products of a user based on user ID.
    """
    user = collection.find_one({"userID": user_id}, {"_id": 0, "purchasedClothes": 1})

    if not user or "purchasedClothes" not in user:
        return jsonify({"error": "User not found or has no purchased products"}), 404

    return jsonify({"userID": user_id, "purchasedProducts": user["purchasedClothes"]})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
