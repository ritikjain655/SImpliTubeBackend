from django.contrib import admin
from django.urls import path
from .views import generate_content,isallwell

urlpatterns = [
    path('api/generate/', generate_content),
    path('alliswell',isallwell)
]
