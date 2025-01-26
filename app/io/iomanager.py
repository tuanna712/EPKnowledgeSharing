import os

from app.connection.mongodb import MongoConnector
from typing import List
from abc import ABC, abstractmethod
from django.core.files.uploadedfile import UploadedFile
from app.document import PdfDocument


class BaseManager(ABC):
    """
    A base class for all managers. Abstract methods interact with django File object.
    """

    def __init__(self):
        pass

    @abstractmethod
    def update_properties(self, uuid: str, content: dict, file_type: str):
        """
        Function to update file associated with UUID.
        Args:
            uuid: string-like representation of UUID of the file. Can be obtained by `str(UUID)`.
            content: a Python dictionary contains update information.
            file_type: type of file to help the database query process. Can only be "image", "table", "text" or "file".

        Returns:
            boolean: `True` if successfully update the databases' entry, and `False` otherwise.
        """
        pass

    @abstractmethod
    def delete(self, uuid: str, file_type: str):
        """
        Delete a file with associated UUID.
        Args:
            uuid: string-like representation of UUID of the file. Can be obtained by `str(UUID)`
            file_type: type of file to help the database query process. Can only be "image", "table", "text" or "file".

        Returns:
            boolean: `True` if successfully delete a databases' entry, and `False` otherwise.
        """
        pass

    @abstractmethod
    def insert(self, document: PdfDocument):
        """
        Insert new file to databases. This method wil call `extract()` from PdfExtractor and use the PdfDocument
        instance to obtain information. Finally, it uploads file with images, tables, and text to MongoDB.
        Args:
            document: A PdfDocument instance that already processed from user's uploaded file
        """
        pass


class IOManager(BaseManager):
    """
    In and Out manager for handling CRUD requests from users. When this class receives a request, it will make changes
    to all other managers it contains. This is good for synchronizing between databases. Hence, all changes to the
    databases should be made by this class.
    """

    def __init__(self, *args: BaseManager):
        super().__init__()
        self._managers: List[BaseManager] = []
        for arg in args:
            self._managers.append(arg)

    def add_manager(self, manager: BaseManager):
        self._managers.append(manager)

    def managers(self):
        return self._managers

    def remove_manager(self, manager: BaseManager):
        self._managers.remove(manager)

    def __getitem__(self, item):
        return self._managers[item]

    def update_properties(self, uuid: str, content: dict, file_type: str):
        for manager in self._managers:
            manager.update_properties(uuid, content, file_type)

    def delete(self, uuid: str, file_type: str):
        for manager in self._managers:
            is_deleted = manager.delete(uuid, file_type)
        return is_deleted

    def insert(self, document: PdfDocument):
        for manager in self._managers:
            manager.insert(document)


class MongoManager(BaseManager):
    """
    Manager class for MongoDB connection. Changes to databases should not be made by this class but by its superclass
    in order to synchronize between databases.
    """

    def __init__(self,
                 username: str = None):
        """
        Args:
            username: username of the requesting user
        """
        super().__init__()
        self._mongo = MongoConnector(username).get_database()

    def update_properties(self, uuid: str, content: dict, file_type: str):
        data = {"$set": content}
        collection = self._mongo[file_type]
        result = collection.update_one({"_id": uuid}, data)
        if result.modified_count > 0:
            return True
        else:
            return False

    def delete(self, uuid: str, file_type: str):
        collection = self._mongo[file_type]
        result = collection.delete_one({"_id": uuid})
        if result.deleted_count > 0:
            return True
        else:
            return False

    def insert(self, document: PdfDocument):
        if not document.is_extracted:
            raise ValueError("PDF file has not been processed.")

        # Insert single file into MongoDB 'file' collection.
        file_properties = document.properties
        mongo_id = file_properties.pop('id')
        file_properties.update({
            "_id": mongo_id
        })
        file = self._mongo['file'].insert_one(file_properties)
        print("File inserted into MongoDB: {}".format(file.inserted_id))

        # Insert images into MongoDB 'image' collection
        for image in document.get_images():
            image_properties = image.properties
            image_id = image_properties.pop('id')
            image_properties.update({
                "_id": image_id
            })
            result = self._mongo['image'].insert_one(image_properties)
            print("Image inserted into MongoDB: {}".format(result.inserted_id))

        # Insert tables into MongoDB 'table' collection
        for table in document.get_tables():
            table_properties = table.properties
            table_id = table_properties.pop('id')
            table_properties.update({
                "_id": table_id
            })
            result = self._mongo['table'].insert_one(table_properties)
            print("Table inserted into MongoDB: {}".format(result.inserted_id))


class LocalManager(BaseManager):
    """
    Manager class for local files. Changes to databases should not be made by this class but by its superclass
    in order to synchronize between databases.
    """

    def __init__(self, username: str):
        super().__init__()
        self._username = username
        self._root = os.getcwd()
        # while os.path.split(self._root)[-1] != "epdatabase":
        #     self._root = os.path.dirname(self._root)

        self._directory = os.listdir(os.path.join(self._root, "usercontent", username))

    def update_properties(self, uuid: str, content: dict, file_type: str):
        pass

    def delete(self, uuid: str, file_type: str):
        for file in self._directory:
            name, ext = os.path.splitext(file)
            if name == uuid:
                os.remove(os.path.join(self._root, "usercontent", self._username, file))
                print("Removed from user \'{}\': {}".format(os.path.split(self._username)[-1], file))
                return

    def insert(self, document: PdfDocument):
        document.get_extractor().download(self._username)
