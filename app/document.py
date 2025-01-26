from typing import List
from fitz import Rect
from uuid import UUID
from pandas import DataFrame


class Raw:
    def __init__(self, file):
        self._file = file

    def get_metadata(self):
        return self._file.metadata

    def get_metadata_keys(self):
        meta = self._file.metadata
        return [x for x in meta]

    def get_type(self):
        return type(self._file)


class Document:
    """
    Base class for all documents, images, tables,... We will never explicitly instantiate this class.
    """

    def __init__(self, uuid: UUID):
        self.id = str(uuid)
        self.properties = {
            'id': self.id
        }

    def __repr__(self):
        return (f"Document:\n"
                f"{self.properties}")

    def __str__(self):
        return (f"Document"
                f"{self.properties}")


class Image(Document):
    """
    A class for operating on images.
    """

    def __init__(self,
                 uuid: UUID,
                 caption: str,
                 page: int,
                 parent_id: UUID):
        """
        Args:
            uuid: uuid of the image
            caption: caption
            page: index of a page in the parent file that contain the image
            parent_id: uuid of the parent file
        """

        super().__init__(uuid)
        self.rect = None
        self.caption = caption
        self.page = page
        self.parent_id = parent_id
        self.properties.update({
            'type': 'image',
            'caption': self.caption,
            'page': self.page,
            'parent_id': self.parent_id
        })

    def set_rect(self, rect: Rect):
        """
        Function to set rectangle bound of the image on its page index
        for later downloading
        """
        self.rect = rect

    def __repr__(self):
        return (f"Image:\n"
                f"{self.properties}")

    def __str__(self):
        return (f"Image"
                f"{self.properties}")


class Table(Document):
    def __init__(self,
                 uuid: UUID,
                 caption: str,
                 page: int,
                 parent_id: UUID):
        """
        Args:
            uuid: uuid of the table
            caption: caption
            page: index of a page in the parent file that contain the table
            parent_id: uuid of the parent file
        """

        super().__init__(uuid)
        self.rect = None
        self.caption = caption
        self.page = page
        self.parent_id = parent_id
        self.dataframe: DataFrame = None
        self.properties.update({
            'type': 'table',
            'caption': self.caption,
            'page': self.page,
            'parent_id': self.parent_id
        })


    def set_dataframe(self, dataframe):
        self.dataframe = dataframe
        

    def set_rect(self, rect: Rect):
        """
        Function to set rectangle bound of the table on its page index
        for later downloading
        """
        self.rect = rect

    def __repr__(self):
        return (f"Table:\n"
                f"{self.properties}")

    def __str__(self):
        return (f"Table"
                f"{self.properties}")


class Text(Document):
    """
    A class for operating on text.
    """

    def __init__(self,
                 uuid: UUID,
                 content: str,
                 page: int,
                 parent_id: UUID):
        """
        Args:
            uuid: id of the Text object
            content: text content
            page: index of a page in the parent file that contain the text
            parent_id: uuid of the parent file
        """

        super().__init__(uuid)
        self.content = content
        self.page = page
        self.parent_id = parent_id
        self.properties.update({
            'content': self.content,
            'page': self.page,
            'parent_id': self.parent_id
        })

    def __repr__(self):
        return (f"Text:\n"
                f"{self.properties}")

    def __str__(self):
        return (f"Text"
                f"{self.properties}")


class PdfDocument(Document):
    """
    A class for storing PDF documents and some basic operations.
    """

    def __init__(self,
                 uuid: UUID,
                 file_name: str,
                 extractor):
        """
        Args:
            uuid: the uuid of the file
            file_name: name of the file
            extractor: the PdfExtractor instance associated with this PdfDocument
        """

        super().__init__(uuid)
        self.file_name = file_name
        self.images: List[Image] = []
        self.tables: List[Table] = []
        self.text: List[Text] = []
        self.is_extracted = False
        self.is_downloaded = False
        self.properties.update({
            'file_name': self.file_name
        })
        self._extractor = extractor

    def get_extractor(self):
        return self._extractor

    def add_image(self, image: Image):
        self.images.append(image)

    def add_table(self, table: Table):
        self.tables.append(table)

    def add_text(self, text: Text):
        self.text.append(text)

    def get_images(self):
        return self.images

    def get_tables(self):
        return self.tables

    def get_text(self):
        return self.text

    def __repr__(self):
        return (f"PdfDocument:\n"
                f"{self.properties}")

    def __str__(self):
        return (f"PdfDocument"
                f"{self.properties}")
