import os, weaviate
import weaviate.classes as wvc
from weaviate.classes.aggregate import GroupByAggregate
from weaviate.classes.config import (
    Property, 
    DataType, 
    Tokenization,
    Configure,
    VectorDistances,
    Reconfigure,
)

class ClientWeaviate:
    def __init__(self, URL:str="", API_KEY:str="", mode:str="cloud"):
        # Connect to a WCS instance
        if mode == "cloud":
            self.client = weaviate.connect_to_wcs(
                cluster_url=URL,
                auth_credentials=weaviate.auth.AuthApiKey(API_KEY),
                skip_init_checks=True,
                )
        if mode == "local":
            self.client = weaviate.connect_to_local(
                host=URL,
                auth_credentials=weaviate.auth.AuthApiKey(API_KEY),
                skip_init_checks=True,
                )
            
    def get_collection(self, _collection_name):
        return self.client.collections.get(_collection_name)
            
    def get_schema(self): # List all collections
        return self.client.collections.list_all(simple=False)
    
    def connect(self):
        self.client.connect()

    def is_live(self):
        return self.client.is_live()
    
    def is_connected(self):
        return self.client.is_connected()
    
    def disconnect(self):
        self.client.close()

    def delete_collection(self, _collection_name):
        if (self.client.collections.exists(_collection_name)):
            self.client.collections.delete(_collection_name)  # Replace with your collection name
            print("Collection {} deleted!".format(_collection_name))
        else:
            print("Collection {} does not exist!".format(_collection_name))

    def delete_all_collections(self):
        self.client.collections.delete_all()
        print("All collections deleted!")

    def auto_create_collection(self, new_collection_name):
        self.client.collections.create(new_collection_name)
        print(f"Collection created! {new_collection_name}")

    def create_collection(self, new_collection_name, property_list):
        self.client.collections.create(
            new_collection_name,
            vectorizer_config=Configure.Vectorizer.text2vec_openai(), # Using OpenAI
            vector_index_config=Configure.VectorIndex.hnsw(
                dynamic_ef_factor=10,
                distance_metric=VectorDistances.COSINE,
            ), # Set vector index type: "hnsw" or "flat" index types. Compression ("pq" for "hnsw" indexes and "bq" for "flat" indexes)
            inverted_index_config=Reconfigure.inverted_index(
                bm25_k1=1.1,
                bm25_b=0.8
            ),
            # generative_config=Configure.Generative.openai(
            #     model="gpt-3.5-turbo-1106",
            #     max_tokens=2000,
            #     temperature=0.0,
            # ),
            # replication_config=Configure.replication(
            #     factor=3,
            # ), # Configure replication per collection
            properties=property_list,
            # Property(name="title", 
            #     description="Title of the article",
            #     data_type=DataType.TEXT,
            #     vectorize_property_name=True,  # Use "title" as part of the value to vectorize
            #     tokenization=Tokenization.WORD  # Use "word" tokenization
            #     indexFilterable=True,
            #     indexSearchable=True,
            # ),
        )
        
class WVCollection(ClientWeaviate):
    def __init__(self, URL:str="", API_KEY:str="", collection_name:str="demo_collection", mode:str="cloud"):
        super().__init__(URL, API_KEY, mode)
        self.collection_name = collection_name
        if self.client.collections.exists(self.collection_name):
            self.collection = self.client.collections.get(self.collection_name)
            self.total_count = self.collection.aggregate.over_all(total_count=True).total_count
        else:
            print(f"Collection {self.collection_name} does not exist!")

    def get_config(self):
        return self.collection.config.get()
    
    def insert_obj(self, obj_uuid, properties, vector):
        self.collection.data.insert(
            uuid=obj_uuid,
            properties=properties,
            vector=vector,
            # references=wvc.data.Reference("f81bfe5e-16ba-4615-a516-46c2ae2e5a80"),  # If you want to add a reference (if configured in the collection definition)
        )

    def get_object_by_id(self, obj_uuid):
        return self.collection.query.fetch_object_by_id(uuid=obj_uuid)
        
    def update_obj(self, obj_uuid, properties, vector):
        self.collection.data.update(
            uuid=obj_uuid,
            properties=properties,
            vector=vector,
        )

    def replace_obj(self, obj_uuid, properties, vector):
        self.collection.data.replace(
            uuid=obj_uuid,
            properties=properties,
            vector=vector,
        )

    def delete_obj(self, obj_uuid):
        self.collection.data.delete_by_id(uuid=obj_uuid)

    def search(self, 
               user_query, 
               query_vector, 
               limit:str=3, 
               alpha:float=0.25, 
               auto_limit:int=1, 
               filters:wvc.query.Filter=None, 
               ):
        return self.collection.query.hybrid(
            query=user_query,
            # query_properties=["question^2", "answer"], #Specify properties to keyword search - '^2' is a boost/weight factor
            vector=query_vector,
            limit=limit,
            alpha=alpha, #Balance keyword and vector search, 1 is a pure vector search, 0 is a pure keyword search
            fusion_type=wvc.query.HybridFusion.RELATIVE_SCORE, #Change the ranking method - "RANKED" or "RELATIVE_SCORE
            # auto_limit=auto_limit, #Limit results to groups with similar distances from the query,
            filters=filters,
            # filters=wvc.query.Filter.by_property("round").contains_any(["Double Jeopardy!"]), #https://weaviate.io/developers/weaviate/api/graphql/filters#filter-structure
            return_metadata=wvc.query.MetadataQuery(score=True, explain_score=True),
        )
    

#================================================================================================
from weaviate.classes.query import Filter

def get_parent_text(WVClient, parent_id):
    sibling_objects = WVClient.collection.query.fetch_objects(
        filters=Filter.by_property("parent_id").equal(parent_id),
        limit=30
        ).objects
    return _extract_parent_txt(sibling_objects)

def _extract_parent_txt(sibling_objects):
    parent_object = {}
    parent_object['parent_id'] = sibling_objects[0].properties['parent_id']
    parent_object['file_id'] = sibling_objects[0].properties['file_id']
    parent_object['page_num'] = sibling_objects[0].properties['page_num']

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

    def _get_sib_by_id(sibling_objects, _id):
        for sibs in sibling_objects:
            if str(sibs.uuid) == _id:
                return sibs
            
    children_nodes = [_get_sib_by_id(sibling_objects, id) for id in children_ids]
    parent_object['text'] = '\n'.join(re.properties['text'] for re in children_nodes)

    return parent_object

def get_references(search_results, top_k=3):
    parent_ids = list(set([r.properties['parent_id'] for r in search_results]))
    parent_objects = [get_parent_text(parent_id) for parent_id in parent_ids[:top_k]]
    return parent_objects
