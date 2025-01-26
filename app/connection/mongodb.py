from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
import certifi, os
import dotenv; dotenv.load_dotenv()

class MongoConnector:
    """
    Wrapper class for MongoDB database. Must call `get_database()` before interacting.
    """

    def __init__(self, db_name):
        self._db_name = db_name
        __mode = os.getenv("MONGO_MODE")
        if __mode == "local":
            self.client = MongoClient(
                host=os.getenv("MONGO_URI"),
                port=int(os.getenv("MONGO_PORT")),
                username=os.getenv("MONGO_USERNAME"),
                password=os.getenv("MONGO_PASSWORD"),
                # tlsCAFile=certifi.where(),
                )
        elif __mode == "cloud":
            self.client = MongoClient(
                f"mongodb+srv://{os.getenv('MONGO_CLOUD_USERNAME')}:{os.getenv('MONGO_CLOUD_PASSWORD')}@{os.getenv('MONGO_CLOUD_URI')}/?retryWrites=true&w=majority"
            )
        else:
            raise ValueError("Invalid MONGO_MODE")
        
        self._db = self.client[db_name]
        

    def get_database(self):
        return self._db


class MGConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        __mode = os.getenv("MONGO_MODE")
        if __mode == "local":
            self.client = MongoClient(
                host=os.getenv("MONGO_URI"),
                port=int(os.getenv("MONGO_PORT")),
                username=os.getenv("MONGO_USERNAME"),
                password=os.getenv("MONGO_PASSWORD"),
                # tlsCAFile=certifi.where(),
                )
        elif __mode == "cloud":
            self.client = MongoClient(
                f"mongodb+srv://{os.getenv('MONGO_CLOUD_USERNAME')}:{os.getenv('MONGO_CLOUD_PASSWORD')}@{os.getenv('MONGO_CLOUD_URI')}/?retryWrites=true&w=majority"
            )

        self.db = self.client[db_name]

    def get_list_databases(self):
        return list(self.client.list_database_names())

    def delete_database(self, db_name):
        try:
            self.client.drop_database(db_name)
            print(f"Deleted database {db_name}")
        except Exception as e:
            print(e)

    def create_database(self, db_name):
        self.client[db_name]
        print(f"Created database {db_name}")

    def get_list_collections(self):
        return self.db.list_collection_names()

    def delete_collection(self, collection_name):
        try:
            self.db.drop_collection(collection_name)
            print(f"Deleted collection {collection_name}")
        except Exception as e:
            print(e)

    def create_collection(self, collection_name):
        try:
            self.db.create_collection(collection_name)
            print(f"Created collection {collection_name}")
        except Exception as e:
            print(e)


class MGCollection(MGConnection):
    """
    Wrapper class for MongoBD collection.
    """

    def __init__(self, db_name, collection_name):
        """
        Constructor:
        Args:
            db_name (str): name of the database
            collection_name (str): name of the collection
        """
        super().__init__(db_name)
        self.collection_name = collection_name
        self.collection = self.db[self.collection_name]

    def insert_one(self, data):
        try:
            self.collection.insert_one(data)
            print(f"Inserted one document to collection {self.collection_name}")
        except Exception as e:
            print(e)

    def insert_many(self, data):
        try:
            self.collection.insert_many(data)
            print(f"Inserted many documents to collection {self.collection_name}")
        except Exception as e:
            print(e)

    def get_all_docs(self, limit=None):
        if limit is None:
            return self.collection.find()
        else:
            return self.collection.find().limit(limit)

    def get_doc_keys(self):
        return list(self.collection.find_one().keys())

    def get_unique_values(self, key):
        return list(self.collection.distinct(key))

    def delete_doc_by_id(self, id):
        try:
            self.collection.delete_one({"_id": ObjectId(id)})
            print(f"Deleted document with id {id}")
        except Exception as e:
            print(e)

    # Get docs by key, value
    def get_docs_by_key_value(self, key, value):
        return self.collection.find({key: value})

    # Get docs by multiple keys, values
    def get_docs_by_multiple_key_values(self, key_values):
        return self.collection.find(key_values)
