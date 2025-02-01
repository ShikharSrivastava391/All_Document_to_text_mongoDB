import os
import contextlib
from dotenv import load_dotenv
from pathlib import Path
import pymongo
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Any, AsyncIterator
from datetime import datetime


load_dotenv()

class Settings:
    PROJECT_NAME: str = "GirikOcr"
    PROJECT_VERSION: str = "1.0.0"
    DATABASE_URL = os.getenv("CONNECTION_STRING")

class DatabaseSessionManager:
    settings = Settings()

    def __init__(self, engine_kwargs: dict[str, Any] = {}):
        MONGO_DATABASE_URL = self.settings.DATABASE_URL
        self.client = AsyncIOMotorClient(MONGO_DATABASE_URL, **engine_kwargs)
        self.database = self.client["File_extraction"]  # Set database name to "File_extraction"
        self.collection = self.database["collection_001"]  # Set collection name to "collection_001"

    async def create_collections(self):
        # MongoDB creates collections dynamically when data is inserted.
        # No explicit collection creation needed unless you want to do something special.
        pass

    async def close(self):
        if self.client is None:
            raise Exception("DatabaseSessionManager is not initialized")
        self.client.close()
        self.client = None
        self.database = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[pymongo.database.Database]:
        if self.client is None:
            raise Exception("DatabaseSessionManager is not initialized")

        try:
            yield self.database
        except Exception:
            raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[pymongo.collection.Collection]:
        if self.database is None:
            raise Exception("DatabaseSessionManager is not initialized")

        # Use the specified collection "collection_001"
        collection = self.database["collection_001"]  # Set collection name to "collection_001"
        try:
            yield collection
        except Exception:
            raise
        finally:
            pass
        
    # Inside sessionmanager class
    def insert_extracted_text(self, file_name: str, text_data: str):
        print(f"Inserting extracted text into MongoDB: {file_name}")
        # Create a document to insert
        document = {
            "file_name": file_name,
            "extracted_text": text_data,
            "created_at": datetime.utcnow(),  # You can add a timestamp field
        }

        try:
            result =  self.collection.insert_one(document)
            # print(f"Inserted document: {result}")  # Log the inserted document
            print(f"Inserted document with inserted_id: {result.inserted_id}")

        except Exception as e:
            return (f"Error inserting data into MongoDB: {e}")  # Log any errors




sessionmanager = DatabaseSessionManager({"maxPoolSize": 10})  # Example engine kwargs

