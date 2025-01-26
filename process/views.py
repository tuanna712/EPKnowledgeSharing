from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from app.connection.mongodb import MongoConnector
from app.io.iomanager import IOManager, MongoManager, LocalManager
from bson.objectid import ObjectId
import json
import os
from django.conf import settings
from app.io.extractor.pdf_extractor import PdfExtractor

# Create your views here.
def process(request):
    id = request.GET['file']

    database = MongoConnector(request.user.username).get_database()
    file_collection = database['file']
    file = file_collection.find_one({'_id': id})
    file['id'] = file['_id']

    image_collection = database['image']
    images = [image for image in image_collection.find({'parent_id': id})]
    for image in images:
        image['id'] = image['_id']

    table_collection = database['table']
    tables = [table for table in table_collection.find({'parent_id': id})]
    for table in tables:
        table['id'] = table['_id']

    context = {
        'file': file,
        'images': images,
        'tables': tables,
    }
    return render(request, 'process/process.html', context)


def update(request):
    data = json.loads(request.body.decode('utf-8'))
    print(f"Update: {data}")
    id = data['id']

    caption = data['caption']
    page = data['page']
    type = data['type']

    mongo_manager = MongoManager(request.user.username)
    mongo_manager.update_properties(id,
                                    {'caption': caption, 'page': page},
                                    type)
    return HttpResponse("Successfully updated!", status=200)

def delete(request):
    data = json.loads(request.body.decode('utf-8'))
    print(f"Delete {data}")
    id = data['id']
    file_type = data['type']
    
    local_manager = LocalManager(request.user.username)
    mongo_manager = MongoManager(request.user.username)
    manager = IOManager(local_manager, mongo_manager)
    is_deleted = manager.delete(id, file_type)
    print(is_deleted)
    if is_deleted == True:
        return HttpResponse("Delete successfully", status = 200)
    else:
        return HttpResponse("This component is no longer in the databases.", status=200) 

def file_explorer(request):
    if request.user.is_authenticated:
        file_db = MongoConnector(request.user.username).get_database()['file']
        if file_db.count_documents({}) == 0:
            context = {
                'none': 'You do not have any documents to be shown',
            }
        else:
            cursor = file_db.find()
            files = [file for file in cursor]
            for file in files:
                file['id'] = file['_id']

            context = {
                'files': files,
            }
        return render(request, 'process/explorer.html', context)
    else:
        context = {
            'error': 'You have to login in order to use this feature.'
        }
        return render(request, 'process/explorer.html', context)
    

def upload_file(request):
    file = request.FILES.get('file')
    if file:
        handle_upload_file(file, request.user.username)
    return HttpResponseRedirect('/process/explorer')


def handle_upload_file(f, username):
    user_folder = os.path.join(settings.MEDIA_ROOT, username)

    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    path = os.path.join(settings.MEDIA_ROOT, username, f.name)
    with open(path, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    mongo_manager = MongoManager(username)
    local_manager = LocalManager(username)
    manager = IOManager(local_manager, mongo_manager)

    extractor = PdfExtractor(path)
    doc = extractor.extract()
    manager.insert(doc)
