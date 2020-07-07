from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_cinderella, name='home_cinderella'),
    path('cinderella_url/', views.cinderella_url, name='cinderella_url'),
    path('cinderella_url/cinderella_results/', views.cinderella_results, name='cinderella_results'),
    path('upload_cinderella_images/', views.upload_cinderella_images, name='upload_cinderella_images'),
    path('cinderella_url/cinderella_results/clinical_study/', views.check_clinical_study, name='check_clinical_study')
]