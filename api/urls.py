from django.contrib import admin
from django.urls import path
from .views import generate_content
urlpatterns = [
    path('api/generate/', generate_content),
]
