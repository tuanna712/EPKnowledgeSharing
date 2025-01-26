import json, time, os
from django.shortcuts import render
from app.io.chatbot.chabot import QueryVector
from app.io.chatbot.orchestration import Orchestration
from django.http import JsonResponse

from app.connection.weaviate_connection import ClientWeaviate, WVCollection
from app.connection.mongodb import MGCollection
from app.connection.mysql_connection import MSQL

from .functions import *
import dotenv; dotenv.load_dotenv()

def index(request):
    return render(request, 'chat/index.html')

#files/: Get files for filtering. And check if default OPENAI_KEY is still valid. Automatically load with page.
def get_file_list(request):
    MGC = MGCollection(os.getenv("MG_FILE_DATABASE"), os.getenv("MG_FILE_COLLECTION"))
    files = list(MGC.get_all_docs())
    print(f"/chat/files/: LoadPage-GetFileFiltering: Number of Files: {len(files)}")
    _data = []
    for item in files:
        file_id = item.get('file_id')
        file_name = item.get('file_name')
        if file_id and file_name:
            _data.append({'file_id': file_id, 'file_name': file_name})

    # OpenAI KEY
    is_valid = openai_is_valid(os.getenv("OPENAI_API_KEY"))
    print("/chat/files/: ", os.getenv("OPENAI_API_KEY"))
    print(f"/chat/files/: env OpenAI status: {is_valid}")

    return JsonResponse({'files': _data, 'openai_key_status': is_valid})


#refs/: Get references and list of searched files from Vector Database
def get_refs(request):
    # Get params from request
    data_request = json.loads(request.body)
    print(f"/chat/refs/: Settings: {data_request}")
    user_input = data_request['message']
    try:
        num_refs = int(data_request['numRef'])
    except:
        num_refs = 5
    try:
        searching_index = float(data_request['searchCoef'])
    except:
        searching_index = 0.5

    print(f"/chat/refs/: Number of Refs: {num_refs}")

    sort_descending = data_request['sortDescending']
    userOpenAiKey = data_request['userOpenAiKey']
    openaiKeyMode = data_request['openaiKeyMode']
    verifyUserOpenaiKey = data_request['verifyUserOpenaiKey']
    verifySystemOpenaiKey = data_request['verifySystemOpenaiKey']

    # ----------------------------------
    list_files = data_request['list_files']
    print("/chat/refs/: +-+-+-List Files: ", len(list_files))
    # ----------------------------------
    _filter = get_filter(list_files)
    print("/chat/refs/: +-+-+-Files Filters: ", type(_filter))
    # ----------------------------------
    __start_time = time.time()
    print("/chat/refs/: User Input (Get Refs): ", user_input)

    # IF OPENAI KEY IS READY ...
    if  verifySystemOpenaiKey and openaiKeyMode=="system":
        openai_key_status = True
    elif verifyUserOpenaiKey and openaiKeyMode=="user":
        os.environ["OPENAI_API_KEY"] = userOpenAiKey
        openai_key_status = True
    else:
        openai_key_status = False

    if openai_key_status:
        data = {'refNum': 0}
        try:
            chatbot = QueryVector()
            # ----------------------------------
            intent = Orchestration().get_intent(user_input)
            print("/chat/refs/: GetIntent (Orchestration): ",intent)
            # ----------------------------------
            if intent == '"basic"' or intent == 'basic':
                data['intent'] = 'basic'
                data['files' ] = []
            elif intent == '"undefined"' or intent == 'undefined':
                data['intent'] = 'undefined'
                data['files' ] = []
            else:
                print("/chat/refs/: GetIntent: ",intent)
                # ----------------------------------
                refs = chatbot.retrieval(user_input, limit=num_refs, alpha=searching_index, meta_filter=_filter)
                # ----------------------------------
                if sort_descending:
                    refs = sort_refs(refs)
                    print("\n===== Sorted=====")
                # ----------------------------------
                for ref in refs[:num_refs]:
                    print("/chat/refs/: FileID: ", ref['file_id'], "PageNum: ",ref['page_num'])
                    __file_id = ref['file_id']
                    __images = get_images(__file_id, ref['page_num'])
                    images_links = ["https://viendaukhivn.sharepoint.com/" + image['file_link_url'] for image in __images]
                    ref['images'] = images_links
            
                print("/chat/refs/: Search Refs Time: ", time.time() - __start_time)
                data['intent'] = str(intent)
                data['files' ] = refs
                data['refNum' ] = len(refs)
            data['status'] = 'success'
            return JsonResponse(data)
        except Exception as e:
            print("/chat/refs/: Error: ", e)
            data['status'] = 'error'
            data['error'] = str(e) + " - " + "Please try again!"
            return JsonResponse(data)
    else:
        ...
        return

#reply/: Get final answer
def get_chat_reply(request):
    user = {
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
    }

    MYSQL = MSQL()
    __start_time = time.time()
    user_input = json.loads(request.body)
    user_question = user_input['message']
    userOpenAiKey = user_input['userOpenAiKey']
    openaiKeyMode = user_input['openaiKeyMode']
    verifyUserOpenaiKey = user_input['verifyUserOpenaiKey']
    verifySystemOpenaiKey = user_input['verifySystemOpenaiKey']
    userIntent = user_input['intent']

    print("User Input (Chat Reply): ", user_question)
    print("User OpenAI Key: ", userOpenAiKey, "Status: ", verifyUserOpenaiKey)

    # IF OPENAI KEY IS READY ...
    if  verifySystemOpenaiKey and openaiKeyMode=="system":
        openai_key_status = True
    elif verifyUserOpenaiKey and openaiKeyMode=="user":
        os.environ["OPENAI_API_KEY"] = userOpenAiKey
        openai_key_status = True
    else:
        openai_key_status = False

    if openai_key_status:
        try:
            print(f"User Intent: {userIntent}")
            if userIntent == 'basic':
                answer = Orchestration().basic_conversation(user_question)
                data = {'reply': answer,
                        'intent': 'basic'
                        }
            elif userIntent == 'undefined':
                data = {'reply': 'Tôi chưa hiểu câu hỏi của bạn. Hãy hỏi tôi các câu hỏi về lĩnh vực Tìm kiếm thăm dò Dầu khí?',
                        'intent': 'undefined'
                        }
            else:
                chatbot = QueryVector()
                refs = user_input['refs']['files']
                replied = chatbot.chat(user_question, refs)
                print("Generate Ans Time: ", time.time() - __start_time)
                data = {
                    'reply': replied,
                    'intent': userIntent,
                }
            data['status'] = 'success'
            MYSQL.log(user['username'], user['first_name'], user['last_name'], user_question, data['reply'])
            return JsonResponse(data)
        except Exception as e:
            print("Error: ", e)
            data = {
                    'reply': str(e),
                    'status': 'error',
                    'intent': 'basic',
                }
            MYSQL.log(user['username'], user['first_name'], user['last_name'], user_question, data['reply'])
            return JsonResponse(data)
            
    else:
        print("Invalid OpenAI Key. Generate Ans Time: ", time.time() - __start_time)
        data = {
            'reply': "Invalid OpenAI Key",
            'status': 'success'
        }
        MYSQL.log(user['username'], user['first_name'], user['last_name'], user_question, data['reply'])
        return JsonResponse(data)

# checkllm/ Check if added OPENAI_KEY from UI is valid
def check_added_openai_key(request):
    user_input = json.loads(request.body)
    print("OpenAI Key for Check LLM: ", user_input['userOpenAiKey'])
    is_valid = openai_is_valid(user_input['userOpenAiKey'])
    return JsonResponse({'status': is_valid})

# checkdb/ Check if all databases are connected
def check_databases(request):
    # MongoDB
    try: 
        MGC = MGCollection(os.getenv("MG_FILE_DATABASE"), os.getenv("MG_FILE_COLLECTION"))
        mongo_status = True
    except Exception as e:
        print("check_databases(): MongoDB Error: ", e)
        mongo_status = False

    # Weaviate
    try:
        WVClient = WVCollection(collection_name=os.environ["WEAVIATE_COLL_NAME"], 
                                URL=os.environ["WEAVIATE_URL"], 
                                API_KEY=os.environ["WEAVIATE_API_KEY"], 
                                mode=os.environ["WEAVIATE_MODE"]
                                )
        weaviate_status = True
    except Exception as e:
        print("check_databases(): Weaviate Error: ", e)
        weaviate_status = False

    # MySQL
    try:
        MYSQL = MSQL()
        mysql_stauts = True
    except Exception as e:
        print("check_databases(): MySQL Error: ", e)
        mysql_stauts = False

    data = {
            'mongo_status': mongo_status,
            'weaviate_status': weaviate_status,
            'mysql_status': mysql_stauts,
        }
    return JsonResponse(data)