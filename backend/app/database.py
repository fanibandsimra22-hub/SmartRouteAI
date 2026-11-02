"""
database.py

MongoDB Atlas Connection & Collection Management for SmartRoute AI
Provides resilient connection pooling, collection indexing, and a graceful in-memory
fallback adapter so the application functions even when an external Atlas cluster is offline.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.config import settings

logger = logging.getLogger("smartroute.database")

class MemoryCollectionAdapter:
    """
    Lightweight in-memory collection adapter used when MongoDB Atlas is not yet
    configured or unreachable. Ensures guest searching and testing never crash.
    """
    def __init__(self, name: str):
        self.name = name
        self.documents: List[Dict[str, Any]] = []

    def create_index(self, keys, **kwargs):
        # In-memory mock index
        return f"mock_index_{self.name}"

    def insert_one(self, doc: Dict[str, Any]):
        doc_copy = dict(doc)
        if "_id" not in doc_copy:
            doc_copy["_id"] = str(uuid.uuid4())
        self.documents.append(doc_copy)
        
        class InsertResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        return InsertResult(doc_copy["_id"])

    def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for doc in self.documents:
            match = True
            for k, v in filter_dict.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                return dict(doc)
        return None

    def find(self, filter_dict: Optional[Dict[str, Any]] = None, sort=None, limit: int = 100):
        results = []
        for doc in self.documents:
            if not filter_dict:
                results.append(dict(doc))
            else:
                match = True
                for k, v in filter_dict.items():
                    if doc.get(k) != v:
                        match = False
                        break
                if match:
                    results.append(dict(doc))
        if limit:
            results = results[:limit]
        return results

    def delete_one(self, filter_dict: Dict[str, Any]):
        for idx, doc in enumerate(self.documents):
            match = True
            for k, v in filter_dict.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                del self.documents[idx]
                class DeleteResult:
                    deleted_count = 1
                return DeleteResult()
        class DeleteResult:
            deleted_count = 0
        return DeleteResult()

    def count_documents(self, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        if not filter_dict:
            return len(self.documents)
        return len([d for d in self.documents if all(d.get(k) == v for k, v in filter_dict.items())])


class MemoryDatabaseAdapter:
    """In-memory database adapter for offline/fallback mode."""
    def __init__(self, name: str):
        self.name = name
        self.collections: Dict[str, MemoryCollectionAdapter] = {}

    def __getitem__(self, name: str) -> MemoryCollectionAdapter:
        if name not in self.collections:
            self.collections[name] = MemoryCollectionAdapter(name)
        return self.collections[name]

    def __getattr__(self, name: str) -> MemoryCollectionAdapter:
        return self.__getitem__(name)


class DatabaseManager:
    """
    Manages MongoDB Atlas lifecycle, connection verification, and collection retrieval.
    """
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
        self.is_connected: bool = False
        self.is_fallback: bool = False
        self.connection_error: Optional[str] = None
        self._memory_db: Optional[MemoryDatabaseAdapter] = None

    def connect(self):
        """Attempts to connect to MongoDB Atlas with a short timeout to prevent blocking."""
        uri = settings.MONGODB_URI
        # Check if URI is a placeholder or default unconfigured local
        is_placeholder = "<username>" in uri or "<password>" in uri

        if is_placeholder:
            logger.warning("MongoDB URI contains placeholder credentials. Initializing fallback storage mode.")
            self._init_fallback("MongoDB Atlas URI contains placeholder credentials (<username>:<password>).")
            return

        try:
            logger.info("Connecting to MongoDB...")
            self.client = MongoClient(
                uri,
                serverSelectionTimeoutMS=2500, # 2.5s fast timeout
                connectTimeoutMS=2500,
                maxPoolSize=20
            )
            # Test connection with a quick ping
            self.client.admin.command("ping")
            self.db = self.client[settings.MONGODB_DB_NAME]
            self.is_connected = True
            self.is_fallback = False
            self.connection_error = None
            logger.info(f"Successfully connected to MongoDB: database='{settings.MONGODB_DB_NAME}'")
            self._ensure_indexes()
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as err:
            logger.warning(f"Could not connect to MongoDB server: {str(err)}. Activating in-memory fallback adapter.")
            self._init_fallback(str(err))

    def _init_fallback(self, reason: str):
        """Initializes fallback in-memory database."""
        self.is_connected = False
        self.is_fallback = True
        self.connection_error = reason
        self._memory_db = MemoryDatabaseAdapter(settings.MONGODB_DB_NAME)
        self.db = self._memory_db
        self._ensure_indexes()
        logger.info("In-memory fallback database initialized successfully. Application features will remain functional.")

    def _ensure_indexes(self):
        """Creates required collection indexes for optimal query performance."""
        try:
            # Users Collection Indexes
            self.db.users.create_index([("email", ASCENDING)], unique=True)
            self.db.users.create_index([("created_at", DESCENDING)])

            # Saved Routes Indexes
            self.db.saved_routes.create_index([("user_id", ASCENDING)])
            self.db.saved_routes.create_index([("created_at", DESCENDING)])

            # Saved Locations Indexes
            self.db.saved_locations.create_index([("user_id", ASCENDING)])
            self.db.saved_locations.create_index([("name", ASCENDING)])

            # Route History Indexes
            self.db.route_history.create_index([("user_id", ASCENDING)])
            self.db.route_history.create_index([("created_at", DESCENDING)])
            logger.info("Database collection indexes initialized.")
        except Exception as err:
            logger.warning(f"Could not initialize collection indexes: {str(err)}")

    def get_collection(self, collection_name: str):
        """Returns a collection handle."""
        if self.db is None:
            self.connect()
        return self.db[collection_name]

    def get_status(self) -> Dict[str, Any]:
        """Returns current database connectivity diagnostics."""
        return {
            "connected": self.is_connected,
            "mode": "mongodb_atlas" if self.is_connected else "in_memory_fallback",
            "database_name": settings.MONGODB_DB_NAME,
            "is_fallback": self.is_fallback,
            "error": self.connection_error,
            "collections": [
                "users",
                "saved_routes",
                "saved_locations",
                "route_history"
            ]
        }

    def close(self):
        """Closes MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.is_connected = False
            logger.info("MongoDB client connection closed.")

# Global Database Manager instance
db_manager = DatabaseManager()

def get_database():
    """Dependency / helper to get database handle."""
    if db_manager.db is None:
        db_manager.connect()
    return db_manager.db
