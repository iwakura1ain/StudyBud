from django.urls import path
from . import views


urlpatterns = [
    path('', views.GetRoutes),
    path('rooms/', views.GetRooms),
    path('rooms/<str:key>', views.GetRoom)

]
