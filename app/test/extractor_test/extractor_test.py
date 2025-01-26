from app.io.extractor.pdf_extractor import PdfExtractor
from app.io.basemanager import MongoManager, IOManager, LocalManager
import os


if __name__ == '__main__':
    extractor = PdfExtractor('test.pdf')
    print(extractor.document.properties)
    # # print("Current:", extractor.document)
    # doc = extractor.extract()
    # mongo_manager = MongoManager("minhden")
    # local_manager = LocalManager("minhden")
    # iomanager = IOManager(local_manager, mongo_manager)
    # # iomanager.insert(doc)
    # iomanager.delete("0af16ea2-db8a-4af4-95df-9ba2d37170bb", "image")


