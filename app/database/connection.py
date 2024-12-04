# app/database/connection.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()


class MongoDBConnection:
    def __init__(self):
        self.client = None
        self.database = None
        # Get Mongo URI from the environment file
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("MONGO_DB_NAME", "resume_optimizer")

    def connect(self):
        try:
            # Create MongoDB client using the provided URI
            self.client = MongoClient(self.mongo_uri)
            self.database = self.client[self.db_name]
            # Check the connection by pinging the database
            result = self.client.admin.command("ping")
            print(f"Connected to MongoDB: {result}")  # Should return {"ok": 1.0} if successful
        except Exception as e:
            print("Error connecting to MongoDB:", e)
            raise e

    def get_database(self):
        if not self.database:
            self.connect()
        return self.database
