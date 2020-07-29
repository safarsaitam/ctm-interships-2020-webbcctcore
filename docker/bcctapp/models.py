from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import int_list_validator

# Create your models here.
class Patient(models.Model):
    first_name = models.CharField(max_length=100,null=True)
    last_name = models.CharField(max_length=100,null=True)
    age = models.IntegerField(null=True)
    birthday = models.CharField(max_length=100)
    surgery_date = models.CharField(max_length=100)
    patient_height = models.IntegerField(null=True)
    patient_weight = models.IntegerField(null=True)
    bra = models.CharField(max_length=100,null=True)
    date_posted = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    n_images = models.IntegerField(null=True)
    team = models.IntegerField(null=True)
    share = models.CharField(validators=[int_list_validator],max_length=100000, null=True)
    # Surgery Type
    C1 = 1
    C2 = 2
    C3 = 3
    M1 = 4
    M2 = 5
    M3 = 6
    M4 = 7
    M5 = 8
    M6 = 9
    M7 = 10

    SURGERY_TYPE_CHOICES = [
        (C1, 'Conservative surgery - unilateral'),
        (C2, 'Conservative surgery with bilateral reduction'),
        (C3, 'Conservative surgery with LD or LICAP / TDAP'),
        (M1, 'Mastectomy with unilateral reconstruction with implant'),
        (M2, 'Mastectomy with unilateral reconstruction with autologous flap'),
        (M3, 'Mastectomy with bilateral reconstruction with implants'),
        (M4,
         'Mastectomy with unilateral reconstruction with implant and contralateral symmetrization with implant (augmentation)'),
        (M5, 'Mastectomy with unilateral reconstruction with implant and contralateral symmetrization with reduction'),
        (M6,
         'Mastectomy with unilateral reconstruction with autologous flap and contralateral symmetrization with reduction'),
        (M7,
         'Mastectomy with unilateral reconstruction with autologous flap and contralateral symmetrisation with implant (augmentation)')
    ]

    surgery_type = models.IntegerField(choices=SURGERY_TYPE_CHOICES)

    def __str__(self):
        return self.first_name

    def get_absolute_url(self):
        return reverse('patient-detail', kwargs={'pk': self.pk})

    def query_set(self,id):
        return Patient(id=id)


class Photo(models.Model):
    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class MedicalImages(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='medical_images/', blank=True, null=True)

    def __str__(self):
        return str('image')


class ImagesPatient(models.Model):
    number = models.IntegerField(null=True)
    image = models.ImageField(upload_to='medical_images4/', blank=True, null=True)
    mime_type = models.CharField(max_length=100,null=True)
    file_type = models.CharField(max_length=100,null=True)
    image_width = models.CharField(max_length=100,null=True)
    image_height = models.CharField(max_length=100,null=True)
    date_created = models.CharField(max_length=100,null=True)
    date_updated = models.CharField(max_length=100,null=True)
    days = models.IntegerField(null=True)
    left_endpoint_x = models.FloatField(null=True)
    left_endpoint_y = models.FloatField(null=True)
    l_breast_contour_2_x = models.FloatField(null=True)
    l_breast_contour_2_y = models.FloatField(null=True)
    l_breast_contour_3_x = models.FloatField(null=True)
    l_breast_contour_3_y = models.FloatField(null=True)
    l_breast_contour_4_x = models.FloatField(null=True)
    l_breast_contour_4_y = models.FloatField(null=True)
    l_breast_contour_5_x = models.FloatField(null=True)
    l_breast_contour_5_y = models.FloatField(null=True)
    l_breast_contour_6_x = models.FloatField(null=True)
    l_breast_contour_6_y = models.FloatField(null=True)
    l_breast_contour_7_x = models.FloatField(null=True)
    l_breast_contour_7_y = models.FloatField(null=True)
    l_breast_contour_8_x = models.FloatField(null=True)
    l_breast_contour_8_y = models.FloatField(null=True)
    l_breast_contour_9_x = models.FloatField(null=True)
    l_breast_contour_9_y = models.FloatField(null=True)
    l_breast_contour_10_x = models.FloatField(null=True)
    l_breast_contour_10_y = models.FloatField(null=True)
    l_breast_contour_11_x = models.FloatField(null=True)
    l_breast_contour_11_y = models.FloatField(null=True)
    l_breast_contour_12_x = models.FloatField(null=True)
    l_breast_contour_12_y = models.FloatField(null=True)
    l_breast_contour_13_x = models.FloatField(null=True)
    l_breast_contour_13_y = models.FloatField(null=True)
    l_breast_contour_14_x = models.FloatField(null=True)
    l_breast_contour_14_y = models.FloatField(null=True)
    l_breast_contour_15_x = models.FloatField(null=True)
    l_breast_contour_15_y = models.FloatField(null=True)
    l_breast_contour_16_x = models.FloatField(null=True)
    l_breast_contour_16_y = models.FloatField(null=True)
    left_midpoint_x = models.FloatField(null=True)
    left_midpoint_y = models.FloatField(null=True)
    right_endpoint_x = models.FloatField(null=True)
    right_endpoint_y = models.FloatField(null=True)
    r_breast_contour_19_x = models.FloatField(null=True)
    r_breast_contour_19_y = models.FloatField(null=True)
    r_breast_contour_20_x = models.FloatField(null=True)
    r_breast_contour_20_y = models.FloatField(null=True)
    r_breast_contour_21_x = models.FloatField(null=True)
    r_breast_contour_21_y = models.FloatField(null=True)
    r_breast_contour_22_x = models.FloatField(null=True)
    r_breast_contour_22_y = models.FloatField(null=True)
    r_breast_contour_23_x = models.FloatField(null=True)
    r_breast_contour_23_y = models.FloatField(null=True)
    r_breast_contour_24_x = models.FloatField(null=True)
    r_breast_contour_24_y = models.FloatField(null=True)
    r_breast_contour_25_x = models.FloatField(null=True)
    r_breast_contour_25_y = models.FloatField(null=True)
    r_breast_contour_26_x = models.FloatField(null=True)
    r_breast_contour_26_y = models.FloatField(null=True)
    r_breast_contour_27_x = models.FloatField(null=True)
    r_breast_contour_27_y = models.FloatField(null=True)
    r_breast_contour_28_x = models.FloatField(null=True)
    r_breast_contour_28_y = models.FloatField(null=True)
    r_breast_contour_29_x = models.FloatField(null=True)
    r_breast_contour_29_y = models.FloatField(null=True)
    r_breast_contour_30_x = models.FloatField(null=True)
    r_breast_contour_30_y = models.FloatField(null=True)
    r_breast_contour_31_x = models.FloatField(null=True)
    r_breast_contour_31_y = models.FloatField(null=True)
    r_breast_contour_32_x = models.FloatField(null=True)
    r_breast_contour_32_y = models.FloatField(null=True)
    r_breast_contour_33_x = models.FloatField(null=True)
    r_breast_contour_33_y = models.FloatField(null=True)
    right_midpoint_x = models.FloatField(null=True)
    right_midpoint_y = models.FloatField(null=True)
    sternal_notch_x = models.FloatField(null=True)
    sternal_notch_y = models.FloatField(null=True)
    left_nipple_x = models.FloatField(null=True)
    left_nipple_y = models.FloatField(null=True)
    right_nipple_x = models.FloatField(null=True)
    right_nipple_y = models.FloatField(null=True)
    # View Type
    AP = 1
    LE = 2
    LD = 3
    VIEW_TYPE_CHOICES = [
        (AP, 'Anterior Posterior'),
        (LE, 'Lateral Esquerda'),
        (LD, 'Lateral Direita'),
    ]
    view_type = models.IntegerField(choices=VIEW_TYPE_CHOICES, null=True, blank=True,default=0)
    CE = 1
    MM = 2
    IMG_TYPE_CHOICES = [
        (CE, 'Classificação Estéticca'),
        (MM, 'Mamografia'),
    ]
    img_type = models.IntegerField(choices=IMG_TYPE_CHOICES, null=True, blank=True,default=0)

    def __str__(self):
        return str('image')


class InteractionsPatient(models.Model):
    number = models.IntegerField(null=True)
    image_id = models.IntegerField(null=True)
    author = models.IntegerField(null=True)
    image = models.ImageField(upload_to='medical_images4/', blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    interaction_type = models.CharField(max_length=30)


class Teams(models.Model):
    name = models.CharField(max_length=100)
    number = models.IntegerField(null=True)
    users =  models.CharField(validators=[int_list_validator],max_length=10000000)
    patients = models.CharField(validators=[int_list_validator],max_length=10000000)

