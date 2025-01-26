import weaviate.classes as wvc
from app.connection.mongodb import MGCollection
from app.connection.openai_connection import MyOAI


def get_images(file_id, page_num):
    page_nums = [int(page_num) + i for i in range(-2, 3)]
    MongoImages = MGCollection("FileProcessingManager", "processed_image_database")
    filter = {
        "parent_id": file_id,
        "page": {'$in':page_nums}
    }
    images = list(MongoImages.get_docs_by_multiple_key_values(filter))
    return images

def sort_refs(refs):
    year = {}
    for i, _dict in enumerate(refs):
        year[i] = _dict.get('year')
    sorted_order = []
    sorted_year = []
    year_int_dict = {}
    for k,v in year.items():
        if v is None:
            sorted_order.append(k)
        else:
            sorted_year.append(int(v))
            year_int_dict[k] = int(v)
    sorted_year.sort()  
    for i in sorted_year:
        for k,v in year_int_dict.items():
            if int(v) == i:
                sorted_order.append(k)
            
    sorted_refs = [refs[i] for i in sorted_order[::-1]]
    return sorted_refs

def get_filter(list_files):
    # Check if list_files is empty
    if len(list_files) == 0:
        return None
    else:
        file_ids = [list_files[i] for i in range(len(list_files)) if len(list_files[i]) > 5]
        if len(file_ids) == 0:
            return None
        else:
            filters=wvc.query.Filter.by_property("file_id").contains_any(file_ids)
            return filters
        
def openai_is_valid(openai_key):
    """
    Check if the OPENAI_KEY is valid
    """
    try:
        MOAI = MyOAI(openai_key)
        embeddings = MOAI.get_embedding("Hello world")
        return True
    except:
        return False
    
    