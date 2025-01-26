from app.connection.connectors import Connector
import pandas as pd

def main():
    TARGETED_URL = '/sites/NV-HiptracuTiliuTmkimthmd/Shared Documents/General/Database/SongHong Basin/For ChatBot'

    # meta = Connector().get_metadata(TARGETED_URL)

    SPConnector = Connector.to_sharepoint()
    
    file_urls = SPConnector.get_file_links_inside_folder(TARGETED_URL)

    print("Totoal files inside folder: ",len(file_urls))

    df = pd.DataFrame()

    for i, url in enumerate(file_urls):
        print("\nGetting file meta: ", i,"\nURL:", url)
        file_meta = SPConnector.get_metadata(url)
        # Read file_meta (dict) to pandas df
        _df = pd.DataFrame(file_meta, index=[-1])
        # pd concat df and _df
        df = pd.concat([df, _df], axis=0, ignore_index=True)

    # Save df to JSON
    LOCAL_FILE_URL_JSON = 'app/database/tabular/file_information.json'
    df.to_json(LOCAL_FILE_URL_JSON, orient='records')

    return file_meta

def main2():
    from app.io.extractor.pdf_extractor import PdfExtractor

    extractor = PdfExtractor('app/test/extractor_test/table_test.pdf')
    document = extractor.document

    extractor.extract_images()
    for image in extractor.document.images:
        print(image.properties)

    # table_list = extractor.extract_table()
    # print(document.tables[0])

if __name__ == '__main__':
    main2()