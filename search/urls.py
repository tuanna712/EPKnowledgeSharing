from . import views
from django.urls import path

app_name = "search"

urlpatterns = [
    path('', views.results, name='results'),
    path('library/', views.library, name="library"),
    path('library/filter/', views.filter, name="filter"),
]