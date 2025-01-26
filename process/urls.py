from django.urls import path
from .views import process, update, delete, file_explorer, upload_file

app_name = 'process'

urlpatterns = [
    path("" , process, name='index'),
    path("update/", update, name='update'),
    path("delete/", delete, name="delete"),
    path("explorer/", file_explorer, name="explorer"),
    path("upload/", upload_file, name="upload"),
]