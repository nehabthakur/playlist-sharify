import logging

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


class MongoHelper:
    def __init__(self, credentials: dict[str, str]):
        self._credentials = credentials
        self._client = self._establish_connection()

    def _establish_connection(self) -> MongoClient:
        username = self._credentials['username']
        password = self._credentials['password']
        cluster_id = self._credentials['cluster_id']
        return MongoClient(f"mongodb+srv://{username}:{password}@{cluster_id}")

    def list_databases(self) -> list[dict]:
        return [db for db in self._client.list_databases()]

    def _get_database(self, database: str) -> Database:
        return self._client.get_database(database)

    def _get_collection(self, database: str, collection: str) -> Collection:
        self.create_collection(database, collection)
        return self._get_database(database).get_collection(collection)

    def create_collection(self, database: str, collection: str) -> None:
        db = self._get_database(database)
        if collection not in db.list_collection_names():
            db.create_collection(collection)

    def insert_doc(self, database: str, collection: str, record: dict[str, any]) -> None:
        if '_id' not in record:
            logging.warning(f'_id not set for {database}.{collection}')

        collection = self._get_collection(database, collection)
        collection.replace_one({"_id": record["_id"]}, record, upsert=True)

    def get_doc(self, database: str, collection: str, query: dict[str, any]) -> dict[str, any] | None:
        collection = self._get_collection(database, collection)
        return collection.find_one(query)

    def delete_doc(self, database: str, collection: str, query: dict[str, any]) -> None:
        collection = self._get_collection(database, collection)
        collection.delete_one(query)

    def close(self):
        self._client.close()
