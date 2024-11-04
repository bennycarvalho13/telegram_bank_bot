from pymongo import MongoClient
from datetime import datetime
from config import MONGO_URI, DATABASE_NAME, COLLECTION_NAME

# Establish connection
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
users = db[COLLECTION_NAME]

# Test connection by inserting a sample document
def test_connection():
    try:
        users.insert_one({"test": "connection successful"})
        print("MongoDB connection is successful!")
        # Clean up the test document after testing
        users.delete_one({"test": "connection successful"})
    except Exception as e:
        print("Error connecting to MongoDB:", e)

if __name__ == "__main__":
    test_connection()

def get_user_data(user_id):
    user = users.find_one({"user_id": user_id})
    if not user:
        # Initialize user data
        user = {
            "user_id": user_id,
            "balance": 0,
            "last_transaction": None,
            "methods": []  # List of deposit/withdrawal methods
        }
        users.insert_one(user)
    return user

def update_balance(user_id, amount, transaction_type):
    user = get_user_data(user_id)
    new_balance = user["balance"] + amount if transaction_type == "deposit" else user["balance"] - amount
    transaction = {
        "amount": amount,
        "type": transaction_type,
        "timestamp": datetime.now()
    }
    users.update_one({"user_id": user_id}, {
        "$set": {
            "balance": new_balance,
            "last_transaction": transaction
        }
    })
