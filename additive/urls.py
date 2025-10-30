from os import name

from django.urls import path

from . import views

urlpatterns = [
    path("search-additive/", views.search_additive, name="search_additive"),
    path("search-ingredient/", views.search_ingredient, name="search_ingredient"),
    path("add-ingredient/", views.add_ingredient, name="add_ingredient"),
    path("add-additive/", views.add_additive, name="add_additive"),
]
