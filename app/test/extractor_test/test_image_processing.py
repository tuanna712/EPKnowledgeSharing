from app.connection.mongodb import MGCollection
from app.io.extractor.pdf_extractor import PdfExtractor
from app.connection.qdrant_connection import MyQdrant


# from app.connection.weaviate_connection import MyWeaviate


def save_file_info(FileManager, PDFFile):
    _file_info = PDFFile.document._info
    del _file_info['file_uuid']
    result = FileManager.collection.find_one(_file_info)
    if result is None:
        FileManager.insert_one(_file_info)
        print("Imported file information to DB")
        _result = FileManager.collection.find_one(_file_info)
        print("Read File UUID from DB: ", str(_result['_id']))
        PDFFile.document._info['file_uuid'] = str(_result['_id'])
        print("Updated file information, current file id: ", PDFFile.document._info['file_uuid'])
    else:
        print("File already exist in DB")
        print("File UUID from DB: ", str(result['_id']))
        PDFFile.document._info['file_uuid'] = str(result['_id'])
        print("Updated file information, current file id: ", PDFFile.document._info['file_uuid'])

    return PDFFile


def save_image_info(ImageManager, PDFFile):
    # Update Image information to ImageManager
    images = PDFFile.document.images
    for img in images:
        image_info = img.properties
        image_info.update({'caption_type': 'image'})
        image_info.update({'file_uuid': PDFFile.document._info['file_uuid']})
        # print(image_info)
        if ImageManager.collection.find_one(image_info) is None:
            ImageManager.insert_one(image_info)
        else:
            print("Image already exist in DB")


def save_table_info(TableManager, PDFFile):
    # Update Image information to ImageManager
    tables = PDFFile.document.tables
    for table in tables:
        table_info = table.properties
        table_info.udpate({'caption_type': 'table'})
        table_info.update({'file_uuid': PDFFile.document._info['file_uuid']})
        # print(table_info)
        if TableManager.collection.find_one(table_info) is None:
            TableManager.insert_one(table_info)
        else:
            print("Table already exist in DB")


def main():
    db_name = "USER1"
    file_collection_name = "files_database"
    image_collection_name = "images_database"
    table_collection_name = "tables_database"
    DOWNLOAD_IMAGES_URL = 'app/database/images'
    DOWNLOAD_TABLE_URL = 'app/database/tables'

    file_path = "usercontent/minhden/test_image_table.pdf"
    PDFFile = PdfExtractor(file_path)
    # print(PDFFile.document._info)

    # Define connection to MongoDB
    FileManager = MGCollection(db_name, file_collection_name)
    ImageManager = MGCollection(db_name, image_collection_name)
    TableManager = MGCollection(db_name, table_collection_name)

    # Save file information to MongoDB
    # PDFFile = save_file_info(FileManager, PDFFile)

    # Extract images from PDF file
    # PDFFile.extract_images(DOWNLOAD_IMAGES_URL)
    # save_image_info(ImageManager, PDFFile)

    # Extract table from PDF file
    # PDFFile.extract_tables(DOWNLOAD_TABLE_URL)
    # save_table_info(TableManager, PDFFile)

    # Extract text from PDF file
    # PDFFile.extract_text()
    # pages = PDFFile.document.text
    # for page in pages[15:17]:
    #     print(page.properties['page_num'])
    #     print(page.properties['content'])


if __name__ == '__main__':
    main()
