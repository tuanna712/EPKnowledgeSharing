from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.index, name="index"),
    path('reply/', views.get_chat_reply, name="reply"),
    path('refs/', views.get_refs, name="refs"),
    path('files/', views.get_file_list, name="files"),
    path('checkllm/', views.check_added_openai_key, name="checkllm"),
    path('checkdbs/', views.check_databases, name="checkdbs")
]