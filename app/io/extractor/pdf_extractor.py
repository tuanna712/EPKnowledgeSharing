import fitz
import uuid
from uuid import UUID
from app.document import PdfDocument
from app.document import Image, Table, Text
from fitz import Rect, Point, IRect
from fitz import Pixmap
import os
from typing import List, Tuple

# STATIC VARIABLES
CAPTION_START_WORDS = ['figure', 'image', 'ảnh', 'minh', 'hình', 'picture', 'bảng', 'fig', 'summary', 'table']

ROOT = os.getcwd()
# while os.path.split(ROOT)[-1] != "epdatabase":
#     ROOT = os.path.dirname(ROOT)


# STATIC METHODS
def _check_valid_caption(text: str) -> bool:
    """
    Helper function to check if a text starts with valid caption convention
    such as 'figure', 'image', 'anh', 'minh hoa', 'hinh', ...
    Args:
        text (str)

    Returns:
        bool: True if this text is valid caption, and False otherwise.
    """
    text = text.strip()
    if not text:
        return False
    text = text.lower()
    text = text.split()[0]
    return any(text == i for i in CAPTION_START_WORDS)


def check_split_image(rect1: Rect,
                      rect2: Rect) -> bool:
    """
    Helper function to check if two images are actually split parts of one large image.
    Args:
        rect1 (Rect): Rectangle bound of image 1
        rect2 (Rect): Rectangle bound of image 2

    Returns:
        bool: True if the images are join-able, or false otherwise.
    """

    eps = 20
    if abs(rect1.y1 - rect2.y0) < eps or \
            abs(rect1.x1 - rect2.x0) < eps or \
            abs(rect1.x0 - rect2.x1) < eps or \
            abs(rect1.y0 - rect2.y1) < eps or \
            rect1.intersects(rect2):
        return True
    else:
        # Use these to debug
        # print("x1 - x0: {} - {} = {}".format(rect1.x1, rect2.x0, rect1.x1 - rect2.x0))
        # print("x0 - x1: {} - {} = {}".format(rect1.x0, rect2.x1, rect1.x0 - rect2.x1))
        # print("y0 - y1: {} - {} = {}".format(rect1.y0, rect2.y1, rect1.y0 - rect2.y1))
        # print("y1 - y0: {} - {} = {}".format(rect1.y1, rect2.y0, rect1.y1 - rect2.y0))
        return False


def join_rects(join_list: list) -> Rect:
    """
    Helper function to join list of Rects into one large Rect
    Args:
        join_list: list of Rects

    Returns:
        large_rect: Rectangle object
    """

    x = []
    y = []
    for rect in join_list:
        x.append(rect.x0)
        x.append(rect.x1)
        y.append(rect.y0)
        y.append(rect.y1)
    return Rect(min(x), min(y), max(x), max(y))


def download_image(pixmap: Pixmap,
                   rect: Rect,
                   username: str,
                   id: UUID) -> str:
    """
    Function to download image within a bound.
    Args:
        pixmap (Pixmap): pixmap context
        rect (Rect): Rectangle bound for the image
        username: name of the user request
        id : UUID instance of the file
    """
    try:
        i_rect = rect.irect
        pix = Pixmap(pixmap, pixmap.width, pixmap.height, i_rect)
        saved_path = os.path.join(ROOT, "usercontent", username, "{}.png".format(str(id)))
        pix.save(saved_path)
        return saved_path
    except AttributeError as e:
        print(e)
        pass


def _get_all_images_rects_on_one_page(image_list: list,
                                      page: fitz.Page) -> list:
    """
    Helper function to find split image fragments and join them.
    Args:
        image_list (list): List of images in one page.
        page (fitz.Page): a fitz.Page document

    Returns:
        list: list of Rects represent joined images.
    """

    rect_list = []
    img_idx = 0
    idx = 0
    while img_idx in range(0, len(image_list)) and len(image_list) > 1:
        rect1 = page.get_image_rects(image_list[img_idx])[0]
        rect2 = page.get_image_rects(image_list[img_idx + 1])[0]
        join_list = [rect1]
        while check_split_image(rect1, rect2):
            join_list.append(rect2)
            idx += 1
            if idx >= len(image_list) - 1:
                break
            rect1 = page.get_image_rects(image_list[idx])[0]
            rect2 = page.get_image_rects(image_list[idx + 1])[0]
        large_rect = join_rects(join_list)
        rect_list.append(large_rect)
        idx += 1
        img_idx = idx
        if img_idx >= len(image_list) - 1:
            break
    if len(image_list) == 1:
        rect_list.append(page.get_image_rects(image_list[0])[0])
    elif len(image_list) == 0:
        return rect_list
    return rect_list


class PdfExtractor:
    """
    A class for extracting from PDF file.


    Attributes
    -----------
    file_name : str.
        link to the pdf file.
    pdf_file : fitz.Document
        a fitz.Document object to interact with pdf file.
    document : Document object.
        Document object.

    Methods
    -------
    get_caption(rect, page_index)
        Get the caption of a specific image in a page.

    """

    # DEFAULT INDEXES
    TEXT_BLOCK_X0 = 0
    TEXT_BLOCK_Y0 = 1
    TEXT_BLOCK_X1 = 2
    TEXT_BLOCK_Y1 = 3
    TEXT_BLOCK_CAPTION = 4

    def __init__(self,
                 file_path: str):
        """
        Parameters:
            file_path (str): link to a file.

        """

        # Rename the file to id
        dir_path, self.file_name = os.path.split(file_path)
        __, ext = os.path.splitext(self.file_name)
        temp_id = uuid.uuid4()
        new_file_path = os.path.join(dir_path, f"{str(temp_id)}{ext}")
        os.rename(file_path, new_file_path)
        self.file_path = new_file_path
        self.pdf_file = fitz.open(self.file_path)
        self.document = PdfDocument(temp_id, self.file_name, self)
        self.document.properties.update(self.get_file_info())

    def get_file_info(self):
        return {
            "file_name": self.file_name,
            "file_ext": self.file_name.split('.')[-1],
            "file_size": os.path.getsize(self.file_path),
            "file_pages": self.pdf_file.page_count,
            "file_metadata": self.pdf_file.metadata,
            "file_path": self.file_path,
        }

    def download(self, username: str):
        """
        Function to download all images, tables and text to local server.
        If PDF Document hasn't been process, this method will throw an exception.
        Args:
            username: name of the user request
        """

        if not self.document.is_extracted:
            raise Exception("PdfDocument has not been extracted.")

        for image in self.document.get_images():
            pixmap = self.pdf_file[image.page - 1].get_pixmap()
            download_image(pixmap, image.rect, username, image.id)
            print("Image downloaded: {}".format(image.id))

        for table in self.document.get_tables():
            pixmap = self.pdf_file[table.page - 1].get_pixmap()
            download_image(pixmap, table.rect, username, table.id)
            print("Table downloaded: {}".format(table.id))
        self.document.is_downloaded = True

    def extract(self) -> PdfDocument:
        """
        Extract all information, images, tables, and text.

        Returns:
            document: instance of PdfDocument class after extracting.
        """

        self.extract_images()
        self.extract_tables()
        self.extract_text()
        self.document.is_extracted = True
        return self.document

    def extract_images(self) -> List[Image]:
        """
        Core function to extract images in a PDF file.
        For each image extracted, this function create an Image object 
        and append to image list in Document.

        Returns:
            List[Image]: list of images in document
        """

        # Go through all pages.
        for page_idx in range(0, len(self.pdf_file)):
            page = self.pdf_file[page_idx]
            # Initiate pixmap
            image_list = page.get_images()
            rect_list = _get_all_images_rects_on_one_page(image_list, page)
            print("Page: {}".format(page_idx + 1))
            # print(rect_list)
            # Go through all rect in the page.
            for rect in rect_list:
                caption = self.get_caption(rect, page_idx)
                print('Processing image:', caption)
                image = Image(uuid.uuid4(),
                              caption,
                              page_idx + 1,
                              self.document.id)
                image.set_rect(rect)
                # Append image into image list in Document object.
                self.document.add_image(image)
        return self.document.images

    def _check_text_inside_image(self,
                                 rect: Rect,
                                 text_block: list) -> bool:
        """
        Helper function to check if a text box is inside an image or a table.

        Args:
            rect (Rect): fitz.Rectangle bound of the image or table.
            text_block (list): a list representation of text block.

        Returns:
            bool: True if the text is inside the image, and False otherwise.
        """

        text_rect = Rect(text_block[self.TEXT_BLOCK_X0],
                         text_block[self.TEXT_BLOCK_Y0],
                         text_block[self.TEXT_BLOCK_X1],
                         text_block[self.TEXT_BLOCK_Y1])
        return rect.contains(text_rect)

    def _get_closest_caption_block(self,
                                   rect: Rect,
                                   text_blocks: list) -> list:
        """
        Helper function to get the closest text block to the image.

        Args:
            rect (Rect): Rectangle bound of the image or table.
            text_blocks (list): list of text blocks

        Returns:
            list: nearest text block to the image represent by list
        """

        eps_y = 80
        image_center = Point(
            (rect.x0 + rect.x1) / 2,
            (rect.y0 + rect.y1) / 2
        )
        min_distance = 1000.0
        min_idx = 0
        for idx, block in enumerate(text_blocks, start=0):
            if self._check_text_inside_image(rect, block):
                continue
            block_center = Point(
                (block[self.TEXT_BLOCK_X0]
                 + block[self.TEXT_BLOCK_X1]) / 2,
                (block[self.TEXT_BLOCK_Y0]
                 + block[self.TEXT_BLOCK_Y1]) / 2
            )
            distance = image_center.distance_to(block_center)
            if distance < min_distance:
                min_distance = distance
                min_idx = idx

        if rect.y0 - text_blocks[min_idx][self.TEXT_BLOCK_Y1] > eps_y or \
                text_blocks[min_idx][self.TEXT_BLOCK_Y0] - rect.y1 > eps_y:
            return None
        return text_blocks[min_idx]

    def _valid_caption(self, text_blocks) -> list:
        """
        Helper function to get valid captions from text blocks in a page.
        Args:
            text_blocks: all text blocks in one page

        Returns:
            list of valid caption blocks.
        """

        valid_captions = []
        for block in text_blocks:
            if _check_valid_caption(block[self.TEXT_BLOCK_CAPTION]):
                valid_captions.append(block)
        if len(valid_captions) == 0:
            return None
        else:
            return valid_captions

    def get_caption(self,
                    img_rect: Rect,
                    page_idx: int) -> str:
        """
        Gets the caption of an image.

        Args:
            img_rect (Rect): Rect bound of the image.
            page_idx (int): page number.

        Returns:
            str: caption of the image.
        """

        page = self.pdf_file[page_idx]
        text_blocks = page.get_text('blocks')

        try:
            text_blocks = self._valid_caption(text_blocks)
            block = self._get_closest_caption_block(img_rect, text_blocks)

            # Normalize captions
            caption = block[self.TEXT_BLOCK_CAPTION].replace('\n', '')
            caption = caption.replace(':', '.')
            caption = caption.replace('/', '_')
            return caption.strip()

        except Exception as e:
            print("Exception:", e)

    def extract_tables(self):
        for page_idx in range(len(self.pdf_file) - 1):
            page = self.pdf_file[page_idx]
            try:
                print("Page:", page_idx)
                table_list = page.find_tables()
                for table in table_list:
                    rect = Rect(table.bbox)
                    caption = self.get_caption(rect, page_idx)
                    dataframe = table.to_pandas()
                    print("Processing table:", caption)
                    table = Table(uuid.uuid4(),
                                  caption,
                                  page_idx + 1,
                                  self.document.id)
                    table.set_rect(rect)

                    # Set dataframe for table
                    table.set_dataframe(dataframe)
                    
                    self.document.add_table(table)
            except Exception as e:
                print(e)
                pass
        return self.document.tables

    def extract_text(self):
        import re
        for page_idx in range(0, len(self.pdf_file)):
            page = self.pdf_file[page_idx]
            content = page.get_text()
            # Remove redundant whitespace and newline
            # text = re.sub(r'\s+', ' ', text).strip()
            text = Text(uuid.uuid4(),
                        content,
                        page_idx + 1,
                        self.document.id)
            self.document.add_text(text)

        return self.document.text
