import os
from dotenv import load_dotenv
# env_path = load_dotenv(os.path.join(BASE_DIR, '.env'))
# load_dotenv(env_path)
# load_dotenv(".env")
# os.environ.pop('WEAVIATE_COLL_NAME')
# load_dotenv(".env")
from app.connection.weaviate_connection import WVCollection
from app.connection.openai_connection import MyOAI
from weaviate.classes.query import Filter
import warnings
warnings.filterwarnings("ignore")

class QueryVector:
    def __init__(self):
        URL = os.environ["WEAVIATE_URL"]
        print("WEAVIATE URL: ", URL)
        API_KEY = os.environ["WEAVIATE_API_KEY"]
        WEAVIATE_COLL_NAME = "EPDB"
        WEAVIATE_MODE = os.environ["WEAVIATE_MODE"]
        
        self.WVClient = WVCollection(collection_name=WEAVIATE_COLL_NAME, URL=URL, API_KEY=API_KEY, mode=WEAVIATE_MODE)
        self.OAI = MyOAI(os.environ.get('OPENAI_API_KEY'))
        self.system = "You are an VPI - an AI assistant developed by Vietnam Petroleum Institue that helps people find information."
        self.parent_objects = []

    def chat(self, userInput, parent_objects):
        full_text = "\n\nContext: \n\n"
        for i in range(len(parent_objects)):
            if MyOAI.token_count(full_text) < 8096:
                # print(f"{parent_objects[i]['text'][:100]}")
                full_text += parent_objects[i]['text'] + "\n\n"
            else:
                print(f"===Using {i} references===")
                break
            # full_text = "\n\nContext: ".join(re['text'] for re in parent_objects)
        self.prompt = """
        You are master in summarizing and answering questions by the given context and references.
        Always answer using information from the context and references. If the context and references are not enough, say you don't have enough information.
        Always answer in Vietnamese.
        Question: {}
        Referecences: {}
        """.format(userInput, full_text)
        print(f"\nPrompt Token = {MyOAI.token_count(self.prompt)}\n---First 100 characters of Prompt: {self.prompt[:100]}\n")
        self.chat_response = self.OAI.get_chat(prompt=self.prompt, 
                                     system=self.system,
                                     )
        print('Got OpenAI answer!')
        return self.chat_response

    def retrieval(self, userInput, limit:int=10, alpha:float=0.5, meta_filter=None):
        query_vector = self.OAI.get_embedding(userInput)
        self.search_results = self.WVClient.search(userInput, query_vector, limit=limit, alpha=alpha, filters=meta_filter).objects
        self.parent_objects = self.__get_references(self.search_results)
        return self.parent_objects

    def __get_references(self, search_results):
        parent_ids = []
        for r in search_results:
            try:
                parent_ids.append(r.properties['parent_id'])
            except Exception as e:
                print("Can't get parent_id", e)
        parent_ids = list(set(parent_ids))
        parent_objects = [self.__get_parent_text(parent_id) for parent_id in parent_ids]
        return parent_objects

    def __get_parent_text(self, parent_id):
        sibling_objects = self.WVClient.collection.query.fetch_objects(
            filters=Filter.by_property("parent_id").equal(parent_id),
            limit=30
            ).objects
        return self.__extract_parent_txt(sibling_objects)

    def __extract_parent_txt(self, sibling_objects):
        parent_object = {}
        parent_object['parent_id'] = sibling_objects[0].properties['parent_id']
        parent_object['file_id'] = sibling_objects[0].properties['file_id']
        parent_object['page_num'] = sibling_objects[0].properties['page_num']
        try:
            parent_object['file_redirect_url'] = sibling_objects[0].properties['serverRedirectedEmbedUrl']
        except Exception as e:
            parent_object['file_redirect_url'] = None
            print("Can't get file_redirect_url", e)
        parent_object['file_name'] = sibling_objects[0].properties['file_name']
        try:
            parent_object['year'] = sibling_objects[0].properties['yearOfPublication']
        except Exception as e:
            parent_object['year'] = None
            print("Can't get yearOfPublication", e)

        for sib in sibling_objects:
            if "previous_id" not in list(sib.properties.keys()):
                sib.properties['previous_id'] = None

        #Mapping the result order to a dictionary
        _order = {str(sibs.uuid): sibs.properties['previous_id'] for sibs in sibling_objects}

        #Get ID of the first child
        children_ids = [k for k, v in _order.items() if v is None]

        #Store the ID of the previous child
        _targeted_id = children_ids[0]

        # Loop through the order dictionary to get the matched children IDs
        len_ord = 1
        while len_ord < len(_order):
            for k, v in _order.items():
                if v == _targeted_id:
                    _targeted_id = k
                    children_ids.append(k)
                    len_ord += 1

        def __get_sib_by_id(sibling_objects, _id):
            for sibs in sibling_objects:
                if str(sibs.uuid) == _id:
                    return sibs
                
        children_nodes = [__get_sib_by_id(sibling_objects, id) for id in children_ids]
        parent_object['text'] = '\n'.join(re.properties['text'] for re in children_nodes)

        return parent_object

