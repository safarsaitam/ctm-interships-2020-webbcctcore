from django import forms
from .models import Photo, MedicalImages, Patient, ImagesPatient, InteractionsPatient, Teams
import datetime

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ('file',)


class FileFieldForm(forms.Form):
    images = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))


class MedicalImagesForm(forms.ModelForm):
    class Meta:
        model = MedicalImages
        fields = ('image',)

class DateInput(forms.DateInput):
    input_type = 'date'

class PatientForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    age = forms.IntegerField(min_value=0)
    birthday = forms.DateField(input_formats=['%d/%m/%Y'],widget = DateInput)
    surgery_date = forms.DateField(input_formats=['%d/%m/%Y'],widget = DateInput)
    patient_height = forms.IntegerField(min_value=1)
    patient_weight = forms.IntegerField(min_value=1)
    bra=forms.CharField(max_length=100)
    images = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = Patient
        fields = ('first_name','last_name','images','age','patient_weight','patient_height','bra','surgery_type','surgery_date','birthday',)

class ImagesForm(forms.ModelForm):
    image = forms.ModelMultipleChoiceField(queryset=Patient.objects.all())

    class Meta:
        model = ImagesPatient
        fields = ('image',)

class InteractionsPatientForm(forms.ModelForm):
    number = forms.IntegerField()
    interaction_type = forms.IntegerField()

    class Meta:
        model = InteractionsPatient
        fields = ('number','interaction_type',)

class TeamsForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    users = forms.CharField(max_length=100)
    patients = forms.CharField(max_length=100)

    class Meta:
        model = Teams
        fields = ('name','users',)


class ContactForm(forms.Form):
    name = forms.CharField(required = True)
    email = forms.EmailField(required = True)
    content = forms.CharField(required = False, max_length=1024, widget=forms.Textarea(attrs={"rows":6, "cols":20}))
    CHOICES = (('1', '',), ('2', '',),('3', '',), ('4', '',),('5',''))
    score = forms.ChoiceField(required = True, widget=forms.RadioSelect, choices=CHOICES)
