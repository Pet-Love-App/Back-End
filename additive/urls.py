from django.urls import path

from . import views

urlpatterns = [
    path("search-additive/", views.search_additive, name="search_additive"),
    path("search-ingredient/", views.search_ingredient, name="search_ingredient"),
]
