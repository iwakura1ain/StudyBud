from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

from . import views


urlpatterns = [
    path("", views.HomeView, name="home"),
    path("topics/", views.TopicsView, name="topics"),
    path("activities/", views.ActivitiesView, name="activities"),
    path("room/<str:key>/", views.RoomView, name="room_view"),
    path("create-room/", views.RoomCreate, name="room_creation"),
    path("update-room/<str:key>/", views.RoomUpdate, name="room_update"),
    path("delete-room/<str:key>/", views.RoomDelete, name="room_deletion"),
    path("delete-message/<str:key>", views.MessageDelete, name="delete_message"),
    path("login/", views.LoginView, name="login_view"),
    path("register/", views.RegisterView, name="register_view"),
    path("logout/", views.LogoutView, name="logout_view"),
    path("profile/<str:key>", views.ProfileView, name="profile_view"),
    path("profile-edit/<str:key>", views.ProfileEditView, name="profile_edit")
]
