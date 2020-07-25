from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:room_name>/', views.room, name='room'),
    path('room/<str:room_name>/<str:person_name>/', views.ShowChatPage, name = "showchat"),


]