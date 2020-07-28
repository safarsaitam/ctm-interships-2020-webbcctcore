from django.urls import path
from . import views
from .views import GroupCreateView, GroupUpdateView

app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),
    path('room/<int:room_name>/', views.ShowChatPage, name = "show-chat"),
    path('room/', views.ShowChatPage, kwargs={'room_name': None}, name = "show-chat"),
    path('room/new/', GroupCreateView.as_view(), name = "group-create"),
    path('room/<int:pk>/update', GroupUpdateView.as_view(), name = "group-update"),
    path('get/ajax/loadMessages/', views.loadMessage, name = "load-messages")


]