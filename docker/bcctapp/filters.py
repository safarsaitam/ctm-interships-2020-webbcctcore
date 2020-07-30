import django_filters
from .models import Patient, Teams
from django import forms
from django.contrib.auth.models import User


class PatientFilter(django_filters.FilterSet):

    id = django_filters.NumberFilter(widget=forms.NumberInput(attrs={ 'min': '1'}))
    age = django_filters.NumberFilter(widget=forms.NumberInput(attrs={ 'min': '0'}))

    class Meta:
        model = Patient

        fields = {
            'first_name' : ['icontains'],
            'age' : ['exact'],
            'id' : ['exact']

        }


class TeamFilter(django_filters.FilterSet):

    id = django_filters.NumberFilter(widget=forms.NumberInput(attrs={ 'min': '0'}))


    class Meta:
        model = Teams

        fields = {
            'name' : ['icontains'],
            'id' : ['exact']
        }
