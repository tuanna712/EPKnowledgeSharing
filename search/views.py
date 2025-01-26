from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from app.connection.connectors import Connector
from app.connection.mongodb import MGCollection
import json

db_name = "SharePointManager"
collection_name = "files_database"
MGC = MGCollection(db_name, collection_name)

def results(request):
    search_text = request.GET.get('search_text')
    option = request.GET.get('search_option')
    search_fields = [
        'ReportAuthor',
        'Name',
    ]

    index_fields = [(field, 'text') for field in search_fields]
    MGC.collection.drop_indexes()
    MGC.collection.create_index(index_fields, default_language="none")
    search_query = {"$text": {"$search": search_text}}
    results = MGC.collection.find(search_query, {"score": {"$meta": "textScore"}}).sort([("score", {"$meta": "textScore"})])

    docs = [doc for doc in results]

    # Normalize _id fields
    for doc in docs:
        doc['_id'] = str(doc['_id'])
        print(doc.keys())

    filter_list = [
        'Basin',
        'Block',
        'Fields',
        'WellName',
        'Contractors',
        'YearOfPublication',
        'StatusOfReport',
        'TypesOfReport',
        'TypeofFormat',
        'ReportAuthor',
    ]
        
    filters = {}
    for f in filter_list:
        filters.update({
            f: MGC.get_unique_values(f)
        })

    context = {
        'filters': filters,
        'search_text': search_text,
        'search_option': option,
        'search_fields': search_fields,
        'number_of_results': len(docs),
        'docs': docs,
    }
    return render(request, 'search/results.html', context)

def library(request):
    if request.method == "GET":
        filter_list = [
            'Basin',
            'Block',
            'Fields',
            'WellName',
            'Contractors',
            'YearOfPublication',
            'StatusOfReport',
            'TypesOfReport',
            'TypeofFormat',
            'ReportAuthor',
        ]
        
        filters = {}
        for f in filter_list:
            filters.update({
                f: MGC.get_unique_values(f)
            })

        docs = MGC.get_all_docs(limit=15)
        context = {
            'filters': filters,
            'docs': docs,
        }
        return render(request, 'search/library.html', context)
    else:
        return render(request, 'search/library.html', context)
    
def filter(request):
    post = json.loads(request.body)
    print(post)
    filter = {}
    for key in post:
        filter.update({
            key : {'$in':post[key]}
        })
    results = MGC.get_docs_by_multiple_key_values(filter)
    docs = [doc for doc in results]

    # Normalize _id fields
    for doc in docs:
        doc['_id'] = str(doc['_id'])
    return JsonResponse(docs, safe=False)
