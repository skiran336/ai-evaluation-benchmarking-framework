from typing import Any
from pymongo import MongoClient, DESCENDING
from pymongo.collection import Collection


class RunRepository:
    def __init__(self, uri: str, database: str):
        self.client = MongoClient(uri, serverSelectionTimeoutMS=2500)
        self.collection: Collection = self.client[database]["evaluation_runs"]

    def ping(self) -> None:
        self.client.admin.command("ping")

    def ensure_indexes(self) -> None:
        self.collection.create_index([("created_at", DESCENDING)])
        self.collection.create_index("suite_name")
        self.collection.create_index("model_name")

    def insert(self, document: dict[str, Any]) -> None:
        self.ensure_indexes()
        self.collection.insert_one(document)

    def list_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        docs = self.collection.find({}, {"_id": 0}).sort("created_at", DESCENDING).limit(limit)
        return list(docs)

    def get(self, run_id: str) -> dict[str, Any] | None:
        return self.collection.find_one({"id": run_id}, {"_id": 0})
