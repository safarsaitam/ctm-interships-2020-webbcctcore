from django.urls import path
from .views import PatientDetailView, PatientCreateView, PatientUpdateView, PatientDeleteView, UserPatientListView, \
    ImagePatientUpdateView, PatientSharedDetailView, InteractionsDetailView, TeamsCreateView, \
    MyTeamsListView,TeamListView
from . import views
from django.conf.urls import include



urlpatterns = [
    path('', views.bcctapphome, name='bcctapp-home'),
    path('contact/', views.contact, name='bcctapp-contact'),
    # path('chat/', views.chat, name='bcctapp-chat'),
    path('patient/<int:pk>/', PatientDetailView.as_view(), name='patient-detail'),
    path('team/', TeamsCreateView.as_view(), name='teams-detail'), #done
    path('my_teams/', TeamListView.as_view(), name='my-teams'), #done
    path('myteam/<str:name>', MyTeamsListView.as_view(), name='my-team'), #done
    path('patient/new/', PatientCreateView.as_view(), name='patient-new'), #done
    path('patient/shared/<int:pk>', PatientSharedDetailView.as_view(), name='patient-shared'), #not used
    path('patient/<int:pk>/update/', PatientUpdateView.as_view(), name='patient-update'), #done
    path('patient/<int:pk>/update-image/', ImagePatientUpdateView.as_view(), name='patient-update-image'), #done
    path('patient/<int:pk>/delete/', PatientDeleteView.as_view(), name='patient-delete'), #done
    path('image/<int:pk>/<int>/', InteractionsDetailView.as_view(), name='interaction-form'), #done
    path('user/<str:username>', UserPatientListView.as_view(), name='user-patient'), #done
    path('about/', views.about, name='bcctapp-about'), #done (repetida)
    #path('medical_image_upload/', views.upload_medical_image, name='medical-image-upload'),
    #path('medical_image_modal', views.medical_image_modal, name='medical-image-modal'),
    #path('medical_image_modal/<int:pk>/<int>/', views.medical_image_modal, name='medical-image-modal'),
    path('model/<int:pk>/<int>/', views.medical_image_modal, name='model'), #cant do anything
    path('plot/<int:pk>/<int>/', views.plot_image_modal, name='plot'), #envia me po bcctcore
    path('bcctcore/<int:pk>/<int>/', views.bcctcore, name='bcctcore'),
    path('bcctcore/updateBra/', views.update_breast_bra, name='update_breast_bra'),
    path('patient/images/download', views.download_image, name = 'download-images')
    
]