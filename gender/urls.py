from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("search", views.search, name="search"),
    path("contribute", views.contribute, name="contribute"),
    path("suggest", views.suggest, name="suggest"),
    path("results", views.results, name="results"),
]
