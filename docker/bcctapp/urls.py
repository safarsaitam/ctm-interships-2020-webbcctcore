from django.urls import path
from .views import PatientDetailView, PatientCreateView, PatientUpdateView, PatientDeleteView, UserPatientListView, \
    ImagePatientUpdateView, PatientSharedDetailView, InteractionsDetailView, TeamsCreateView, \
    MyTeamsListView
from . import views

urlpatterns = [
    path('', views.bcctapphome, name='bcctapp-home'),
    path('contact/', views.contact, name='bcctapp-contact'),
    path('chat/', views.chat, name='bcctapp-chat'),
    path('patient/<int:pk>/', PatientDetailView.as_view(), name='patient-detail'),
    path('team/', TeamsCreateView.as_view(), name='teams-detail'),
    path('myteam/<str:name>', MyTeamsListView.as_view(), name='my-team'),
    path('patient/new/', PatientCreateView.as_view(), name='patient-new'),
    path('patient/shared/<int:pk>', PatientSharedDetailView.as_view(), name='patient-shared'),
    path('patient/<int:pk>/update/', PatientUpdateView.as_view(), name='patient-update'),
    path('patient/<int:pk>/update-image/', ImagePatientUpdateView.as_view(), name='patient-update-image'),
    path('patient/<int:pk>/delete/', PatientDeleteView.as_view(), name='patient-delete'),
    path('image/<int:pk>/<int>/', InteractionsDetailView.as_view(), name='interaction-form'),
    path('user/<str:username>', UserPatientListView.as_view(), name='user-patient'),
    path('about/', views.about, name='bcctapp-about'),
    #path('medical_image_upload/', views.upload_medical_image, name='medical-image-upload'),
    #path('medical_image_modal', views.medical_image_modal, name='medical-image-modal'),
    #path('medical_image_modal/<int:pk>/<int>/', views.medical_image_modal, name='medical-image-modal'),
    path('model/<int:pk>/<int>/', views.medical_image_modal, name='model'),
    path('plot/<int:pk>/<int>/', views.plot_image_modal, name='plot'),
    path('bcctcore/<int:pk>/<int>/', views.bcctcore, name='bcctcore'),
    path('bcctcore/updateBra/', views.update_breast_bra, name='update_breast_bra'),
    path('patient/images/download', views.download_image, name = 'download-images')
    
]