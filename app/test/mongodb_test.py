from app.connection.mongodb import MGCollection
from app.io.extractor.pdf_extractor import PdfExtractor


class MongoTest:
    def __init__(self, 
                 pdf: PdfExtractor,
                 db_name: str):
        """
        Class to interact with MongoDB.

        """

        self.pdf = pdf
        self.db_name = db_name
        self.file_manager = MGCollection(self.db_name, "files_database")
        self.image_manager = MGCollection(self.db_name, "images_database")
        self.table_manager = MGCollection(self.db_name, "tables_database")

    def _save_file_info(self) -> None:
        """
        Private function to save files info to MongoDB.
        """

        _file_info = self.pdf.document._info
        del _file_info['file_uuid']
        result = self.file_manager.collection.find_one(_file_info)
        if result is None:
            self.file_manager.insert_one(_file_info)
            _result = self.file_manager.collection.find_one(_file_info)
            self.pdf.document.properties['file_uuid'] = str(_result['_id'])
        else:
            self.pdf.document.properties['file_uuid'] = str(result['_id'])

    def _save_images_info(self) -> None:
        """
        Private function to save images info to MongoDB.
        """

        images = self.pdf.document.images
        for img in images:
            image_info = img.properties
            image_info.update({'caption_type': 'image'})
            image_info.update({'file_uuid':self.pdf.document.properties['file_uuid']})
            if self.image_manager.collection.find_one(image_info) is None:
                self.image_manager.insert_one(image_info)
    
    def _save_tables_info(self) -> None:
        """
        Private function to save tables info to MongoDB.
        """

        tables = self.pdf.document.tables
        for table in tables:
            table_info = table.properties
            table_info.update({'caption_type': 'table'})
            table_info.update({'file_uuid':self.pdf.document.properties['file_uuid']})
            if self.table_manager.collection.find_one(table_info) is None:
                self.table_manager.insert_one(table_info)
    
    def save(self) -> None:
        """
        Function to save all information, images, and tables of the file.
        """

        self._save_file_info()
        self._save_images_info()
        self._save_tables_info()
