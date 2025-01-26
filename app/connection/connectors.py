from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.files.system_object_type import FileSystemObjectType
from office365.sharepoint.listitems.listitem import ListItem
import os

SP_URL = "https://viendaukhivn.sharepoint.com/sites/NV-HiptracuTiliuTmkimthmd"
CLIENT_ID = "1827dcec-f70c-485a-8656-00de50def291"
CLIENT_SECRET = "wGBRmRhkECMOK7QowJL78UAPLIFZcgg5rGIm8sHVpFQ="


class Connector(object):
    @classmethod
    def to_sharepoint(cls):
        return _SharePointConnector()


class _SharePointConnector(Connector):

    # Using Singleton pattern to only connect to Share Point once.
    _instance = None

    def __new__(cls):
        if not isinstance(cls._instance, cls):
            cls._instance = super(_SharePointConnector, cls).__new__(cls)
            cls._ctx = ClientContext(SP_URL).with_credentials(ClientCredential(CLIENT_ID, CLIENT_SECRET))
            cls.file_links, cls.folder_links = cls._instance._get_all_files_links()
        return cls._instance

    def get_file(self, target_url):  # get list of files under url
        """
        Get file from SharePoint
        :param target_url: str
        :return: File
        """
        try:
            file = self._ctx.web.get_file_by_server_relative_url(target_url)
            self._ctx.load(file)
            self._ctx.execute_query()
            return file
        except Exception as e:
            print(e)

    def get_metadata(self, target_url):
        """
        Get file information from SharePoint
        :param target_url: str
        :return: dict
        """
        try:
            file = self.get_file(target_url)
            meta = file.properties
            extend_meta = file.listItemAllFields.get()
            self._ctx.execute_query()
            meta.update(extend_meta.properties)
            # Merge two dicts together
            return meta
        except FileNotFoundError as e:
            print(e)

    def _get_all_files_links(self):
        """
        Get all files and folders links (relativeSiteUrl) from SharePoint
        :return: tuple
        """
        doc_lib = self._ctx.web.default_document_library()
        items = (
            doc_lib.items.select(["FileSystemObjectType"])
            .expand(["File", "Folder"])
            .get_all()
            .execute_query()
        )
        file_links = []
        folder_links = []
        for item in items:  # type: int, ListItem
            if item.file_system_object_type == FileSystemObjectType.Folder:
                folder_links.append(item.folder.serverRelativeUrl)
            else:
                file_links.append(item.file.serverRelativeUrl)
        return file_links, folder_links
    
    def get_file_links_inside_folder(self, folder_url):
        """
        Get all file links (relativeSiteUrl) from SharePoint
        :param TARGETED_URL: str
        :return: list
        """
        return [url for url in self.file_links if url.startswith(folder_url)]

    # file_url is the relative url of the file in sharepoint
    def download_file(self, file_url, filename):
        """
        Download file from SharePoint
        :param file_url: str
        :param filename: str
        :return: str
        """
        local_path = os.path.join('search/static/main/cache/', filename)
        with open(local_path, "wb") as local_file:
            file = self._ctx.web.get_file_by_server_relative_url(file_url)
            file.download(local_file)
            self._ctx.execute_query()
        return local_path
