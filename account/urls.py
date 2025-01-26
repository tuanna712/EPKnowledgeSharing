from django.urls import path, include
from .views import get_profile

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('social_auth/', include('social.apps.django_app.urls', namespace="social")),
    path('profile/', get_profile, name='profile')
]