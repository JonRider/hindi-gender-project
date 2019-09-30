from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("search", views.search, name="search"),
    path("contribute", views.contribute, name="contribute"),
]
