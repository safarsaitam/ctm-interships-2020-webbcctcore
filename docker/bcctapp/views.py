import tensorflow
import subprocess
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, request
from .models import Patient, Photo, MedicalImages, ImagesPatient, InteractionsPatient, Teams
from .forms import PhotoForm, MedicalImagesForm, PatientForm, ImagesForm, InteractionsPatientForm, TeamsForm, ContactForm
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.files.storage import FileSystemStorage, default_storage
from utils.utils import keypoint_prediction
import datetime
import numpy as np
import platform
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic.edit import FormView
from django.contrib.auth.models import User
import datetime
from datetime import datetime
import exifread
import PIL.Image
import PIL.ExifTags
from PIL.ExifTags import TAGS
import cv2
import psutil
import sched
import time
from django.template.loader import get_template
from email.message import EmailMessage
from django.core.mail import send_mail
from django.conf import settings
from .filters import PatientFilter, TeamFilter
from django.http import JsonResponse, HttpResponseNotFound
import os
import zipfile
from django.contrib import messages
from io import BytesIO
from django_filters.views import FilterView
import xlwt


scheduler = sched.scheduler(time.time, time.sleep)


def surgeryTypeConverter(i):
    switcher={
        1: "Conservative surgery - unilateral",
        2: "Conservative surgery with bilateral reduction",
        3: "Conservative surgery with LD or LICAP / TDAP ",
        4: "Mastectomy with unilateral reconstruction with implant",
        5: "Mastectomy with unilateral reconstruction with autologous flap",
        6: "Mastectomy with bilateral reconstruction with implants",
        7: "Mastectomy with unilateral reconstruction with implant and contralateral symmetrization with implant(augmentation)",
        8: "Mastectomy with unilateral reconstruction with implant and contralateral symmetrization with reduction",
        9: "Mastectomy with unilateral reconstruction with autologous flap and contralateral symmetrization with reduction",
        10: "Mastectomy with unilateral reconstruction with autologous flap and contralateral symmetrisation with implant(augmentation)",
    }
    return switcher.get(i, "NULL")


def export_users_xls(request):

    if request.method == "POST":
        patient_id = request.POST.get('patient_id')
        if request.POST.get('export-type') == 'xlsx':
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="PatientInfo.xls"'

            wb = xlwt.Workbook(encoding='utf-8')
        # this will make a sheet named Users Data
            ws = wb.add_sheet('Patient Data')

        # Sheet header, first row
            row_num = 0

            font_style = xlwt.XFStyle()
            font_style.font.bold = True

            columns = ['ID', 'First Name', 'Last Name',
                    'Age', 'Weight', 'Height', 'Bra', 'Team', 'Surgery Type', ]

            for col_num in range(len(columns)):
                # at 0 row 0 column
                ws.write(row_num, col_num, columns[col_num], font_style)

            # Sheet body, remaining rows
            font_style = xlwt.XFStyle()

            rows = Patient.objects.filter(pk=patient_id).values_list(
                'id', 'first_name', 'last_name', 'age', 'patient_weight', 'patient_height', 'bra', 'team', 'surgery_type')
            for row in rows:
                row_num += 1
                for col_num in range(len(row)):
                    if col_num == 8:
                        converted_surgery_type = surgeryTypeConverter(row[col_num])
                        ws.write(row_num, col_num, converted_surgery_type, font_style)
                    else:
                        ws.write(row_num, col_num, row[col_num], font_style)

            wb.save(response)

            return response
        return HttpResponseRedirect('/patient/' + patient_id)

    return HttpResponseNotFound('<h1>Invalid request</h1>')


def download_image(request):
    if request.method == "POST":
        patient_id = request.POST.get('patient_id')

        product_images = ImagesPatient.objects.filter(pk=patient_id)

        if product_images.count() == 0:
            return JsonResponse({"message": "No images available to download"})

        filenames = []
        for product_image in product_images:
            filenames.append(str(product_image.image.file))

        # if size is 0 then does nothing
        if len(filenames) == 0:
            messages.add_message(request, messages.INFO, 'No images available')
            return HttpResponseRedirect('/patient/' + patient_id)

        # change
        zip_subdir = "patient_" + patient_id + "_images"
        zip_filename = "%s.zip" % zip_subdir

        s = BytesIO()

        # The zip compressor
        zf = zipfile.ZipFile(s, "w")

        for fpath in filenames:
            # Calculate path for file in zip
            fdir, fname = os.path.split(fpath)
            zip_path = os.path.join(zip_subdir, fname)

            # Add file, at correct path
            zf.write(fpath, zip_path)

        # Must close zip for all contents to be written
        zf.close()
        resp = HttpResponse(
            s.getvalue(), content_type="application/x-zip-compressed")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return resp

    #messages.error(request, 'Invalid request')
    return HttpResponseNotFound('<h1>Invalid request</h1>')


def print_event(name):
    print('EVENT:', time.time(), name)


# Create your views here.


def bcctapphome(request):
    return render(request, 'bcctapp/about.html')
    # return HttpResponse('<h1>BCCTApp Home</h1>')


def get_exif(fn):
    infoDict = {}  # Creating the dict to get the metadata tags

    # For mac and linux user it is just
    exifToolPath = "exiftool"

    imgPath = "/code/media/medical_images4/" + str(fn)

    ''' use Exif tool to get the metadata '''
    process = subprocess.Popen([exifToolPath, imgPath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               universal_newlines=True)
    ''' get the tags in dict '''
    for tag in process.stdout:
        line = tag.strip().split(':')
        infoDict[line[0].strip()] = line[-1].strip()

    return infoDict


class MyTeamsListView(FormView):
    form_class = TeamsForm
    template_name = 'bcctapp/my_team.html'  # Replace with your template.
    success_url = 'my-team'
    print("agora sim")

    def get_context_data(self, request=None, **kwargs):
        print("kw", **kwargs)
        print("self", self.kwargs.get('name'))
        context = super(MyTeamsListView, self).get_context_data(**kwargs)
        teams = Teams.objects.get(name=self.kwargs.get('name'))
        print("teams.id", teams.id)
        context['patient'] = Patient.objects.filter(team=teams.id)
        context['team_id'] = teams.id
        #print("list", list)
        # return render(request, "bcctapp/my_team.html", {'list': list1})
        return context

    def post(self, request, *args, **kwargs):
        print("agora sim tou no post")


class TeamsCreateView(FormView):
    form_class = TeamsForm
    template_name = 'bcctapp/teams.html'  # Replace with your template.
    success_url = 'teams-detail'

    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        name_team = request.POST.get('name_team')
        name = request.POST.get('name')
        print("name", name)
        count = Teams.objects.all().count()
        id_string = " " + str(user_id)
        print(type(id_string))
        if name:
            verify = Teams.objects.filter(name=name)
            print("verify", verify)
            if not verify:
                Teams.objects.create(pk=count, name=name,
                                     users=str(request.user.id))
            else:
                return HttpResponse("This name already exist!")
        else:
            teams = Teams.objects.get(name=name_team)
            if teams is None:
                return HttpResponse("Wrong team name!")
            else:
                flag = False
                for patients in Patient.objects.all():
                    print("owner_id", patients.owner_id, " user_id ", user_id)
                    if int(patients.owner_id) == int(user_id):
                        Patient.objects.filter(owner_id=int(
                            user_id)).update(team=teams.id)
                        print("patients ", patients.id)
                        patients_id = " " + str(patients.id)
                        teams.patients += patients_id
                        teams.save()
                test_user = teams.users
                for s in test_user.split():
                    if s.isdigit() and s == user_id:
                        flag = True
                if flag:
                    return HttpResponse("This user is already added!")
                else:
                    teams.users += id_string
                    teams.save()

        return redirect('user-patient', request.user)


def add_patient(files, x, i, id, current_user):
    for f in files:
        print(i)
        print(files[i])
        if i < x:
            if i == 0:  # certas imagens não tem a data toda e dá erro
                mime_type = ""
                file_type = ""
                image_width = ""
                image_height = ""
                date_created = ""
                try:
                    img = PIL.Image.open("medical_images4/" + files[0])
                    print("imaes", img._getexif().items())
                    if img._getexif().items() is not None:
                        exif = {
                            PIL.ExifTags.TAGS[k]: v
                            for k, v in img._getexif().items()
                            if k in PIL.ExifTags.TAGS
                        }
                    if exif:
                        if 'FileSource' in exif:
                            mime_type = str(exif['FileSource'])
                        if 'ExifImageWidth' in exif:
                            image_width = str(exif['ExifImageWidth'])
                        if 'ExifImageHeight' in exif:
                            image_height = str(exif['ExifImageHeight'])
                        if 'DateTimeOriginal' in exif:
                            date_created = str(exif['DateTimeOriginal'])
                except:
                    print("Image data are outdated.")
                ImagesPatient.objects.create(pk=id, image=files[0], date_created=date_created, mime_type=mime_type,
                                             file_type=file_type, image_width=image_width, image_height=image_height,
                                             number=1)

            if i == 1:
                mime_type = ""
                file_type = ""
                image_width = ""
                image_height = ""
                date_created = ""
                img = PIL.Image.open(files[1])
                try:
                    exif = {
                        PIL.ExifTags.TAGS[k]: v
                        for k, v in img._getexif().items()
                        if k in PIL.ExifTags.TAGS
                    }
                    if exif:
                        if 'FileSource' in exif:
                            mime_type = str(exif['FileSource'])
                        if 'ExifImageWidth' in exif:
                            image_width = str(exif['ExifImageWidth'])
                        if 'ExifImageHeight' in exif:
                            image_height = str(exif['ExifImageHeight'])
                        if 'DateTimeOriginal' in exif:
                            date_created = str(exif['DateTimeOriginal'])
                except:
                    print("Image data are outdated.")
                ImagesPatient.objects.create(pk=id, image=files[1], date_created=date_created, mime_type=mime_type,
                                             file_type=file_type, image_width=image_width, image_height=image_height,
                                             number=2)

            if i == 2:
                mime_type = ""
                file_type = ""
                image_width = ""
                image_height = ""
                date_created = ""
                img = PIL.Image.open(files[2])
                try:
                    exif = {
                        PIL.ExifTags.TAGS[k]: v
                        for k, v in img._getexif().items()
                        if k in PIL.ExifTags.TAGS
                    }
                    if exif:
                        if 'FileSource' in exif:
                            mime_type = str(exif['FileSource'])
                        if 'ExifImageWidth' in exif:
                            image_width = str(exif['ExifImageWidth'])
                        if 'ExifImageHeight' in exif:
                            image_height = str(exif['ExifImageHeight'])
                        if 'DateTimeOriginal' in exif:
                            date_created = str(exif['DateTimeOriginal'])
                except:
                    print("Image data are outdated.")

                ImagesPatient.objects.create(pk=id, image=files[2], date_created=date_created, mime_type=mime_type,
                                             file_type=file_type,
                                             image_width=image_width, image_height=image_height, number=3)

            if i == 3:
                mime_type = ""
                file_type = ""
                image_width = ""
                image_height = ""
                date_created = ""
                img = PIL.Image.open(files[3])
                try:
                    exif = {
                        PIL.ExifTags.TAGS[k]: v
                        for k, v in img._getexif().items()
                        if k in PIL.ExifTags.TAGS
                    }
                    if exif:
                        if 'FileSource' in exif:
                            mime_type = str(exif['FileSource'])
                        if 'ExifImageWidth' in exif:
                            image_width = str(exif['ExifImageWidth'])
                        if 'ExifImageHeight' in exif:
                            image_height = str(exif['ExifImageHeight'])
                        if 'DateTimeOriginal' in exif:
                            date_created = str(exif['DateTimeOriginal'])
                except:
                    print("Image data are outdated.")
                ImagesPatient.objects.create(pk=id, image=files[3], date_created=date_created, mime_type=mime_type,
                                             file_type=file_type,
                                             image_width=image_width, image_height=image_height, number=4)

            if i == 4:
                mime_type = ""
                file_type = ""
                image_width = ""
                image_height = ""
                date_created = ""
                img = PIL.Image.open(files[4])
                try:
                    exif = {
                        PIL.ExifTags.TAGS[k]: v
                        for k, v in img._getexif().items()
                        if k in PIL.ExifTags.TAGS
                    }
                    if exif:
                        if 'FileSource' in exif:
                            mime_type = str(exif['FileSource'])
                        if 'ExifImageWidth' in exif:
                            image_width = str(exif['ExifImageWidth'])
                        if 'ExifImageHeight' in exif:
                            image_height = str(exif['ExifImageHeight'])
                        if 'DateTimeOriginal' in exif:
                            date_created = str(exif['DateTimeOriginal'])
                except:
                    print("Image data are outdated.")
                ImagesPatient.objects.create(pk=id, image=files[4], date_created=date_created, mime_type=mime_type,
                                             file_type=file_type,
                                             image_width=image_width, image_height=image_height, number=5)

                if i == 5:
                    mime_type = ""
                    file_type = ""
                    image_width = ""
                    image_height = ""
                    date_created = ""
                    img = PIL.Image.open(files[5])
                    try:
                        exif = {
                            PIL.ExifTags.TAGS[k]: v
                            for k, v in img._getexif().items()
                            if k in PIL.ExifTags.TAGS
                        }
                        if exif:
                            if 'FileSource' in exif:
                                mime_type = str(exif['FileSource'])
                            if 'ExifImageWidth' in exif:
                                image_width = str(exif['ExifImageWidth'])
                            if 'ExifImageHeight' in exif:
                                image_height = str(exif['ExifImageHeight'])
                            if 'DateTimeOriginal' in exif:
                                date_created = str(exif['DateTimeOriginal'])
                    except:
                        print("Image data are outdated.")
                    ImagesPatient.objects.create(pk=id, image=files[5], date_created=date_created, mime_type=mime_type,
                                                 file_type=file_type,
                                                 image_width=image_width, image_height=image_height, number=6)

                if i == 6:
                    mime_type = ""
                    file_type = ""
                    image_width = ""
                    image_height = ""
                    date_created = ""
                    img = PIL.Image.open(files[6])
                    try:
                        exif = {
                            PIL.ExifTags.TAGS[k]: v
                            for k, v in img._getexif().items()
                            if k in PIL.ExifTags.TAGS
                        }
                        if exif:
                            if 'FileSource' in exif:
                                mime_type = str(exif['FileSource'])
                            if 'ExifImageWidth' in exif:
                                image_width = str(exif['ExifImageWidth'])
                            if 'ExifImageHeight' in exif:
                                image_height = str(exif['ExifImageHeight'])
                            if 'DateTimeOriginal' in exif:
                                date_created = str(exif['DateTimeOriginal'])
                    except:
                        print("Image data are outdated.")
                    ImagesPatient.objects.create(pk=id, image=files[6], date_created=date_created, mime_type=mime_type,
                                                 file_type=file_type,
                                                 image_width=image_width, image_height=image_height, number=7)

        i = i + 1


class PatientCreateView(FormView, RedirectView):
    form_class = PatientForm
    template_name = 'bcctapp/patient_form.html'  # Replace with your template.
    success_url = 'patient-detail'

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('images')
        current_user = request.user
        print(current_user.id)
        if form.is_valid():
            form.save()
            id = form.instance.id
            Patient.objects.filter(pk=id).update(owner=current_user.id)
            i = 0
            x = len(files)
            Patient.objects.filter(pk=id).update(n_images=x)
            add_patient(files, x, i, id, current_user.id)
            return redirect('patient-detail', pk=id)

        return redirect('/cinderella/')


class PatientListView(ListView):
    model = Patient
    template_name = 'bcctapp/home.html'
    context_object_name = 'patients'
    ordering = ['-date_posted']
    paginate_by = 5


class TeamListView(ListView):
    model = Teams
    template_name = 'bcctapp/my_teams.html'
    context_object_name = 'teams'
    paginate_by = 4
    filterset_class = TeamFilter

    def get_queryset(self):
        user = self.request.user.id
        queryset = super().get_queryset().filter(
            users__regex=r'^(\d*[[:space:]]({0})[[:space:]]\d*)|(({0})[[:space:]]\d*)|\d*[[:space:]]({0})|({0})'.format(user))
        print('query')
        print(queryset)
        # self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        # return self.filterset.qs.distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = TeamFilter(
            self.request.GET, queryset=self.get_queryset())
        context['number_results'] = context['filter'].qs.count()
        return context


class UserPatientListView(FilterView, ListView):
    print("entra aqui")
    model = Patient
    template_name = 'bcctapp/user_patients.html'
    context_object_name = 'patients'
    paginate_by = 2
    filterset_class = PatientFilter

    def get_queryset(self):
        queryset = super().get_queryset().filter(owner=self.request.user.id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PatientFilter(
            self.request.GET, queryset=self.get_queryset())
        context['number_results'] = context['filter'].qs.count()
        return context

    def post(self, request, patients_obj=None, *args, **kwargs):
        current_user = request.user
        shared_id = request.POST.get('share_id')
        search = request.POST.get('search')
        name = request.POST.get('name')
        print("name", name)

        if name:
            print("here boy")
            team = Teams.objects.get(name=name)
            if team is None:
                return HttpResponse("This name doesn't exist!")
            else:
                flag = False
                patients = team.patients
                users = team.users
                for s in users.split():
                    print("s", s, "int s ", int(s),
                          " user id ", request.user.id)
                    if s.isdigit() and int(s) == request.user.id:
                        flag = True
                        break
                print("flag", flag)
                if flag:
                    return redirect('my-team', name)
                else:
                    return HttpResponse("You are not member of this team!")
        patient = get_object_or_404(Patient, pk=shared_id)  # verificar o erro
        if patient:
            print("patient")
            check_id = patient.share
            user_id = str(current_user.id)
            flag = False
            if str(patient.owner_id) == user_id:
                flag = True
            if flag == 'False':
                for s in check_id.split():
                    if s.isdigit() and s == user_id:
                        flag = True
            if flag:
                return redirect('patient-detail', pk=shared_id)
            else:
                return HttpResponse("Check your permissions to this Patient!")
        else:
            print("else")
            return HttpResponse("This Patient doesn't exist!")


def view_update(view_type1, view_type2, view_type3, view_type4, view_type5):
    if view_type1:
        ImagesPatient.objects.filter(number=1).update(
            view_type=view_type1)  # first
    if view_type2:
        ImagesPatient.objects.filter(number=2).update(view_type=view_type2)
    if view_type3:
        ImagesPatient.objects.filter(number=3).update(view_type=view_type3)
    if view_type4:
        ImagesPatient.objects.filter(number=4).update(view_type=view_type4)
    if view_type5:
        ImagesPatient.objects.filter(number=5).update(view_type=view_type5)


def img_update(img_type1, img_type2, img_type3, img_type4, img_type5):
    if img_type1:
        ImagesPatient.objects.filter(number=1).update(
            img_type=img_type1)  # first
    if img_type2:
        ImagesPatient.objects.filter(number=2).update(img_type=img_type2)
    if img_type3:
        ImagesPatient.objects.filter(number=3).update(img_type=img_type3)
    if img_type4:
        ImagesPatient.objects.filter(number=4).update(img_type=img_type4)
    if img_type5:
        ImagesPatient.objects.filter(number=5).update(img_type=img_type5)


def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return (d2 - d1).days


class PatientDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Patient
    form_class = PatientForm

    def get_context_data(self, **kwargs):
        print('the person who is in the system is ' + str(self.request.user.id))
        user = User.objects.get(pk=self.request.user.id)
        context = super(PatientDetailView, self).get_context_data(**kwargs)
        patient = Patient.objects.get(pk=self.kwargs['pk'])
        owner = patient.owner
        id = int(self.kwargs['pk'])
        context['patient'] = Patient.objects.get(pk=self.kwargs['pk'])
        for images in ImagesPatient.objects.filter(pk=self.kwargs['pk']):
            if images.date_updated:
                print(patient.surgery_date[:10], images.date_updated)
                x = days_between(
                    str(patient.surgery_date[:10]), str(images.date_updated))
                ImagesPatient.objects.filter(
                    pk=id, number=images.number).update(days=x)
        context['images_patient'] = ImagesPatient.objects.filter(
            pk=self.kwargs['pk'])
        return context

    def post(self, request, *args, **kwargs):
        surgery_type = request.POST.get('surgery_type')
        view_type1 = request.POST.get('view_type1')
        view_type2 = request.POST.get('view_type2')
        view_type3 = request.POST.get('view_type3')
        view_type4 = request.POST.get('view_type4')
        view_type5 = request.POST.get('view_type5')
        img_type1 = request.POST.get('img_type1')
        img_type2 = request.POST.get('img_type2')
        img_type3 = request.POST.get('img_type3')
        img_type4 = request.POST.get('img_type4')
        img_type5 = request.POST.get('img_type5')
        shared_id = request.POST.get('share')
        teamtoshare = request.POST.get('shareteam')
        id = int(self.kwargs['pk'])
        if teamtoshare:
            teamtoshare = int(teamtoshare)
            Patient.objects.filter(pk=id).update(team=teamtoshare)
         # ir buscar o object id e depois atualizar
        view_update(view_type1, view_type2, view_type3, view_type4, view_type5)
        img_update(img_type1, img_type2, img_type3, img_type4, img_type5)

        char2 = ' '
        if shared_id:
            shared_id = char2 + shared_id
            patient = Patient.objects.get(id=id)
            patient.share += shared_id
            patient.save()
        if surgery_type:
            Patient.objects.filter(id=id).update(surgery_type=surgery_type)

        return redirect('patient-detail', pk=id)

    def test_func(self):
        patient = self.get_object()
        if self.request.user == patient.owner:
            return True
        return False


class InteractionsDetailView(LoginRequiredMixin, DetailView):
    model = Patient
    form_class = InteractionsPatientForm
    template_name = 'bcctapp/interaction_form.html'

    def get_context_data(self, **kwargs):
        context = super(InteractionsDetailView,
                        self).get_context_data(**kwargs)
        print('interaction pk filter used: ' + str(self.kwargs['pk']))
        context['interactions'] = InteractionsPatient.objects.filter(
            image_id=self.kwargs['pk'])
        context['users'] = User.objects.all()
        context['images_patient'] = ImagesPatient.objects.filter(
            pk=self.kwargs['pk'])
        context['id'] = int(self.kwargs['int'])
        return context

    def post(self, request, *args, **kwargs):
        interaction_type = request.POST.get('interaction')
        id = self.kwargs['pk']
        print("args", args)
        image_id = int(self.kwargs['int'])
        print(type(image_id))
        current_user = request.user.id
        images_list = []
        i = 1
        for image in ImagesPatient.objects.filter(pk=id):
            images = ImagesPatient.objects.get(pk=id, number=i)
            print("images", images.image)
            images_list.append(images.image)
            i = i + 1
        print("imageslist", images_list[0])
        x = InteractionsPatient.objects.filter(pk=id).count()
        InteractionsPatient.objects.create(
            pk=id, number=x, image=images_list[image_id-1], image_id=image_id, interaction_type=interaction_type, author=current_user)
        print("count", x)
        return redirect('interaction-form', pk=id, int=image_id)


class PatientUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Patient
    fields = ['first_name', 'last_name', 'bra',
              'patient_weight', 'patient_height', 'surgery_type', ]
    template_name = "bcctapp/patient_update.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def test_func(self):
        patient = self.get_object()
        if self.request.user == patient.owner:
            return True
        return False


class ImagePatientUpdateView(LoginRequiredMixin, UserPassesTestMixin, FormView, RedirectView):
    form_class = PatientForm
    template_name = 'bcctapp/patient_update_image.html'

    def get_context_data(self, **kwargs):
        context = super(ImagePatientUpdateView,
                        self).get_context_data(**kwargs)
        context['patient'] = Patient.objects.get(pk=self.kwargs['pk'])
        context['images_patient'] = ImagesPatient.objects.filter(
            pk=self.kwargs['pk'])

        return context

    def post(self, request, *args, **kwargs):
        image = request.POST.get('image')
        image1 = request.POST.get('image1')
        date = str(request.POST.get('date'))
        form_class = self.get_form_class()
        files = request.FILES.getlist('images')
        id = self.kwargs['pk']
        current_user = request.user.id
        if image1 and date:
            ImagesPatient.objects.filter(
                pk=id, number=image1).update(date_updated=date)
        x = ImagesPatient.objects.filter(pk=id).count()
        if files:
            if files[0] and image:
                ImagesPatient.objects.filter(pk=id, number=image).delete()
                mime_type = ""
                file_type = ""
                image_width = ""
                image_height = ""
                date_created = ""
                img = PIL.Image.open(files[0])
                try:
                    exif = {
                        PIL.ExifTags.TAGS[k]: v
                        for k, v in img._getexif().items()
                        if k in PIL.ExifTags.TAGS
                    }
                    if exif:
                        if 'FileSource' in exif:
                            mime_type = str(exif['FileSource'])
                        if 'ExifImageWidth' in exif:
                            image_width = str(exif['ExifImageWidth'])
                        if 'ExifImageHeight' in exif:
                            image_height = str(exif['ExifImageHeight'])
                        if 'DateTimeOriginal' in exif:
                            date_created = str(exif['DateTimeOriginal'])
                except:
                    print("Image data are outdated.")

                ImagesPatient.objects.create(pk=id, image=files[0], date_created=date_created, mime_type=mime_type,
                                             file_type=file_type, image_width=image_width, image_height=image_height,
                                             number=image)

            if files[0] and image is None:
                x += 1
                mime_type = ""
                file_type = ""
                image_width = ""
                image_height = ""
                date_created = ""
                img = PIL.Image.open(files[0])
                try:
                    exif = {
                        PIL.ExifTags.TAGS[k]: v
                        for k, v in img._getexif().items()
                        if k in PIL.ExifTags.TAGS
                    }
                    if exif:
                        if 'FileSource' in exif:
                            mime_type = str(exif['FileSource'])
                        if 'ExifImageWidth' in exif:
                            image_width = str(exif['ExifImageWidth'])
                        if 'ExifImageHeight' in exif:
                            image_height = str(exif['ExifImageHeight'])
                        if 'DateTimeOriginal' in exif:
                            date_created = str(exif['DateTimeOriginal'])
                except:
                    print("Image data are outdated.")

                ImagesPatient.objects.create(pk=id, image=files[0], date_created=date_created, mime_type=mime_type,
                                             file_type=file_type, image_width=image_width, image_height=image_height,
                                             number=x)

        return redirect('patient-detail', pk=id)

    def test_func(self, **kwargs):
        patient = Patient.objects.get(pk=self.kwargs['pk'])
        if self.request.user == patient.owner:
            return True
        return False


class PatientSharedDetailView(DetailView):
    model = Patient
    form_class = PatientForm
    template_name = "bcctapp/patient_shared.html"

    def get_context_data(self, **kwargs):
        context = super(PatientSharedDetailView,
                        self).get_context_data(**kwargs)
        context['patient'] = Patient.objects.get(pk=self.kwargs['pk'])
        context['images_patient'] = ImagesPatient.objects.filter(
            pk=self.kwargs['pk'])

        return context


class PatientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Patient
    success_url = '/'

    def test_func(self):
        patient = self.get_object()
        if self.request.user == patient.owner:
            return True
        return False


def about(request):
    context = {
        'title': 'About'
    }
    return render(request, 'bcctapp/about.html', context)


class BasicUploadView(View):
    def get(self, request):
        photos_list = Photo.objects.all()
        return render(self.request, 'bcctapp/index.html', {'photos': photos_list})

    def patient(self, request):
        form = PhotoForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            photo = form.save()
            data = {'is_valid': True, 'name': photo.file.name,
                    'url': photo.file.url}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)


def upload(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        # print(uploaded_file.name)
        # print(uploaded_file.size)
        fs = FileSystemStorage()
        fs.save(uploaded_file.name, uploaded_file)
    return render(request, 'bcctapp/upload.html')
# File Upload Function


@login_required
def upload_medical_image(request):
    print("funcao print")
    if request.method == 'POST':
        form = MedicalImagesForm(request.POST, request.FILES)
        form.instance.doctor = request.user
        if form.is_valid():
            form.save()
            return redirect('medical-image-modal')
    else:
        form = MedicalImagesForm()
    context = {
        'form': form
    }
    return render(request, 'bcctapp/upload_medical_images.html', context)


def save_kpts(patient_id, number, kpts):
    ImagesPatient.objects.filter(id=patient_id, number=number).update(left_endpoint_x=kpts[0],  # left_endpoint
                                                                      # left_endpoint
                                                                      left_endpoint_y=kpts[1],
                                                                      l_breast_contour_2_x=kpts[2],
                                                                      l_breast_contour_2_y=kpts[3],
                                                                      l_breast_contour_3_x=kpts[4],
                                                                      l_breast_contour_3_y=kpts[5],
                                                                      l_breast_contour_4_x=kpts[6],
                                                                      l_breast_contour_4_y=kpts[7],
                                                                      l_breast_contour_5_x=kpts[8],
                                                                      l_breast_contour_5_y=kpts[9],
                                                                      l_breast_contour_6_x=kpts[10],
                                                                      l_breast_contour_6_y=kpts[11],
                                                                      l_breast_contour_7_x=kpts[12],
                                                                      l_breast_contour_7_y=kpts[13],
                                                                      l_breast_contour_8_x=kpts[14],
                                                                      l_breast_contour_8_y=kpts[15],
                                                                      l_breast_contour_9_x=kpts[16],
                                                                      l_breast_contour_9_y=kpts[17],
                                                                      l_breast_contour_10_x=kpts[18],
                                                                      l_breast_contour_10_y=kpts[19],
                                                                      l_breast_contour_11_x=kpts[20],
                                                                      l_breast_contour_11_y=kpts[21],
                                                                      l_breast_contour_12_x=kpts[22],
                                                                      l_breast_contour_12_y=kpts[23],
                                                                      l_breast_contour_13_x=kpts[24],
                                                                      l_breast_contour_13_y=kpts[25],
                                                                      l_breast_contour_14_x=kpts[26],
                                                                      l_breast_contour_14_y=kpts[27],
                                                                      l_breast_contour_15_x=kpts[28],
                                                                      l_breast_contour_15_y=kpts[29],
                                                                      l_breast_contour_16_x=kpts[30],
                                                                      l_breast_contour_16_y=kpts[31],
                                                                      # left_midpoint
                                                                      left_midpoint_x=kpts[32],
                                                                      # left_midpoint
                                                                      left_midpoint_y=kpts[33],
                                                                      # right_endpoint
                                                                      right_endpoint_x=kpts[34],
                                                                      # right_endpoint
                                                                      right_endpoint_y=kpts[35],
                                                                      r_breast_contour_19_x=kpts[36],
                                                                      r_breast_contour_19_y=kpts[37],
                                                                      r_breast_contour_20_x=kpts[38],
                                                                      r_breast_contour_20_y=kpts[39],
                                                                      r_breast_contour_21_x=kpts[40],
                                                                      r_breast_contour_21_y=kpts[41],
                                                                      r_breast_contour_22_x=kpts[42],
                                                                      r_breast_contour_22_y=kpts[43],
                                                                      r_breast_contour_23_x=kpts[44],
                                                                      r_breast_contour_23_y=kpts[45],
                                                                      r_breast_contour_24_x=kpts[46],
                                                                      r_breast_contour_24_y=kpts[47],
                                                                      r_breast_contour_25_x=kpts[48],
                                                                      r_breast_contour_25_y=kpts[49],
                                                                      r_breast_contour_26_x=kpts[50],
                                                                      r_breast_contour_26_y=kpts[51],
                                                                      r_breast_contour_27_x=kpts[52],
                                                                      r_breast_contour_27_y=kpts[53],
                                                                      r_breast_contour_28_x=kpts[54],
                                                                      r_breast_contour_28_y=kpts[55],
                                                                      r_breast_contour_29_x=kpts[56],
                                                                      r_breast_contour_29_y=kpts[57],
                                                                      r_breast_contour_30_x=kpts[58],
                                                                      r_breast_contour_30_y=kpts[59],
                                                                      r_breast_contour_31_x=kpts[60],
                                                                      r_breast_contour_31_y=kpts[61],
                                                                      r_breast_contour_32_x=kpts[61],
                                                                      r_breast_contour_32_y=kpts[63],
                                                                      r_breast_contour_33_x=kpts[64],
                                                                      r_breast_contour_33_y=kpts[65],
                                                                      # right_midpoint
                                                                      right_midpoint_x=kpts[66],
                                                                      # right_midpoint
                                                                      right_midpoint_y=kpts[67],
                                                                      # sternal_notch
                                                                      sternal_notch_x=kpts[68],
                                                                      # sternal_notch
                                                                      sternal_notch_y=kpts[69],
                                                                      # left_nipple
                                                                      left_nipple_x=kpts[70],
                                                                      # left_nipple
                                                                      left_nipple_y=kpts[71],
                                                                      # right_niple
                                                                      right_nipple_x=kpts[72],
                                                                      right_nipple_y=kpts[73])  # right_niple
    count = InteractionsPatient.objects.filter(pk=patient_id).count()
    InteractionsPatient.objects.create(
        pk=patient_id, number=count+1, interaction_type="keypoints_automatic_detection")


@login_required
def plot_image_modal(request, **kwargs):
    InteractionsPatient.objects.create(
        author=request.user.id, image_id=kwargs.get('pk'), interaction_type='Plot')

    medical_images = ImagesPatient.objects.filter(
        pk=kwargs.get('pk'), number=kwargs.get('int'))
    patient_id = kwargs.get('pk')

    number = kwargs.get('int')
    context = {
        'medical_images': medical_images
    }
    print("entra no plot", patient_id, number)
    img_to_process = get_object_or_404(
        ImagesPatient, pk=patient_id, number=number)
    image = img_to_process.image.url
    print("image", image)
    request.session['image_pk'] = str(patient_id)
    request.session['name'] = image
    request.session['incisura_jugularis_x'] = str(
        img_to_process.sternal_notch_x)
    request.session['incisura_jugularis_y'] = str(
        img_to_process.sternal_notch_y)
    request.session['left_nipple_x'] = str(img_to_process.left_nipple_x)
    request.session['left_nipple_y'] = str(img_to_process.left_nipple_y)
    request.session['right_nipple_x'] = str(img_to_process.right_nipple_x)
    request.session['right_nipple_y'] = str(img_to_process.right_nipple_y)
    request.session['truth_lp_x'] = str(img_to_process.left_endpoint_x)
    request.session['truth_lp_y'] = str(img_to_process.left_endpoint_y)
    request.session['truth_midl_x'] = str(img_to_process.left_midpoint_x)
    request.session['truth_midl_y'] = str(img_to_process.left_midpoint_y)
    request.session['truth_midr_x'] = str(img_to_process.right_midpoint_x)
    request.session['truth_midr_y'] = str(img_to_process.right_midpoint_y)
    request.session['truth_rp_x'] = str(img_to_process.right_endpoint_x)
    request.session['truth_rp_y'] = str(img_to_process.right_endpoint_y)
    # Right Breast Contour
    request.session['l_breast_contour_1_x'] = str(
        img_to_process.left_endpoint_x)
    request.session['l_breast_contour_1_y'] = str(
        img_to_process.left_endpoint_y)
    request.session['l_breast_contour_2_x'] = str(
        img_to_process.l_breast_contour_2_x)
    request.session['l_breast_contour_2_y'] = str(
        img_to_process.l_breast_contour_2_y)
    request.session['l_breast_contour_3_x'] = str(
        img_to_process.l_breast_contour_3_x)
    request.session['l_breast_contour_3_y'] = str(
        img_to_process.l_breast_contour_3_y)
    request.session['l_breast_contour_4_x'] = str(
        img_to_process.l_breast_contour_4_x)
    request.session['l_breast_contour_4_y'] = str(
        img_to_process.l_breast_contour_4_y)
    request.session['l_breast_contour_5_x'] = str(
        img_to_process.l_breast_contour_5_x)
    request.session['l_breast_contour_5_y'] = str(
        img_to_process.l_breast_contour_5_y)
    request.session['l_breast_contour_6_x'] = str(
        img_to_process.l_breast_contour_6_x)
    request.session['l_breast_contour_6_y'] = str(
        img_to_process.l_breast_contour_6_y)
    request.session['l_breast_contour_7_x'] = str(
        img_to_process.l_breast_contour_7_x)
    request.session['l_breast_contour_7_y'] = str(
        img_to_process.l_breast_contour_7_y)
    request.session['l_breast_contour_8_x'] = str(
        img_to_process.l_breast_contour_8_x)
    request.session['l_breast_contour_8_y'] = str(
        img_to_process.l_breast_contour_8_y)
    request.session['l_breast_contour_9_x'] = str(
        img_to_process.l_breast_contour_9_x)
    request.session['l_breast_contour_9_y'] = str(
        img_to_process.l_breast_contour_9_y)
    request.session['l_breast_contour_10_x'] = str(
        img_to_process.l_breast_contour_10_x)
    request.session['l_breast_contour_10_y'] = str(
        img_to_process.l_breast_contour_10_y)
    request.session['l_breast_contour_11_x'] = str(
        img_to_process.l_breast_contour_11_x)
    request.session['l_breast_contour_11_y'] = str(
        img_to_process.l_breast_contour_11_y)
    request.session['l_breast_contour_12_x'] = str(
        img_to_process.l_breast_contour_12_x)
    request.session['l_breast_contour_12_y'] = str(
        img_to_process.l_breast_contour_12_y)
    request.session['l_breast_contour_13_x'] = str(
        img_to_process.l_breast_contour_13_x)
    request.session['l_breast_contour_13_y'] = str(
        img_to_process.l_breast_contour_13_y)
    request.session['l_breast_contour_14_x'] = str(
        img_to_process.l_breast_contour_14_x)
    request.session['l_breast_contour_14_y'] = str(
        img_to_process.l_breast_contour_14_y)
    request.session['l_breast_contour_15_x'] = str(
        img_to_process.l_breast_contour_15_x)
    request.session['l_breast_contour_15_y'] = str(
        img_to_process.l_breast_contour_15_y)
    # Left Breast Contour
    request.session['r_breast_contour_1_x'] = str(
        img_to_process.right_midpoint_x)
    request.session['r_breast_contour_1_y'] = str(
        img_to_process.right_midpoint_y)
    request.session['r_breast_contour_2_x'] = str(
        img_to_process.r_breast_contour_32_x)
    request.session['r_breast_contour_2_y'] = str(
        img_to_process.r_breast_contour_32_y)
    request.session['r_breast_contour_3_x'] = str(
        img_to_process.r_breast_contour_31_x)
    request.session['r_breast_contour_3_y'] = str(
        img_to_process.r_breast_contour_31_y)
    request.session['r_breast_contour_4_x'] = str(
        img_to_process.r_breast_contour_30_x)
    request.session['r_breast_contour_4_y'] = str(
        img_to_process.r_breast_contour_30_y)
    request.session['r_breast_contour_5_x'] = str(
        img_to_process.r_breast_contour_29_x)
    request.session['r_breast_contour_5_y'] = str(
        img_to_process.r_breast_contour_29_y)
    request.session['r_breast_contour_6_x'] = str(
        img_to_process.r_breast_contour_28_x)
    request.session['r_breast_contour_6_y'] = str(
        img_to_process.r_breast_contour_28_y)
    request.session['r_breast_contour_7_x'] = str(
        img_to_process.r_breast_contour_27_x)
    request.session['r_breast_contour_7_y'] = str(
        img_to_process.r_breast_contour_27_y)
    request.session['r_breast_contour_8_x'] = str(
        img_to_process.r_breast_contour_26_x)
    request.session['r_breast_contour_8_y'] = str(
        img_to_process.r_breast_contour_26_y)
    request.session['r_breast_contour_9_x'] = str(
        img_to_process.r_breast_contour_25_x)
    request.session['r_breast_contour_9_y'] = str(
        img_to_process.r_breast_contour_25_y)
    request.session['r_breast_contour_10_x'] = str(
        img_to_process.r_breast_contour_24_x)
    request.session['r_breast_contour_10_y'] = str(
        img_to_process.r_breast_contour_24_y)
    request.session['r_breast_contour_11_x'] = str(
        img_to_process.r_breast_contour_23_x)
    request.session['r_breast_contour_11_y'] = str(
        img_to_process.r_breast_contour_23_y)
    request.session['r_breast_contour_12_x'] = str(
        img_to_process.r_breast_contour_22_x)
    request.session['r_breast_contour_12_y'] = str(
        img_to_process.r_breast_contour_22_y)
    request.session['r_breast_contour_13_x'] = str(
        img_to_process.r_breast_contour_21_x)
    request.session['r_breast_contour_13_y'] = str(
        img_to_process.r_breast_contour_21_y)
    request.session['r_breast_contour_14_x'] = str(
        img_to_process.r_breast_contour_20_x)
    request.session['r_breast_contour_14_y'] = str(
        img_to_process.r_breast_contour_20_y)
    request.session['r_breast_contour_15_x'] = str(
        img_to_process.r_breast_contour_19_x)
    request.session['r_breast_contour_15_y'] = str(
        img_to_process.r_breast_contour_19_y)
    # bcctcore(request)
    #response = HttpResponseRedirect('')
    # return response
    #img = Image.open(img_to_process.image.path)
    #img = cv2.imread(img_to_process.image.path)
    # print(img.shape)
    return redirect('bcctcore', patient_id, number)

    #kpts = keypoint_prediction(img)
    # save_kpts(patient_id,number,kpts)
    #print("kpts", kpts[0], kpts[1])

#    return render(request, 'bcctapp/medical_image_modal.html', context)


def eventFunction0(message):

    print("Executing %s" % message)
# Medical Image List & Predict Keypoints, Plot Keypoints and Delete Image Functions


@login_required
def medical_image_modal(request, **kwargs):
    InteractionsPatient.objects.create(
        author=request.user.id, image_id=kwargs.get('pk'), interaction_type='Predict')
    medical_images = ImagesPatient.objects.filter(
        pk=kwargs.get('pk'), number=kwargs.get('int'))
    patient_id = kwargs.get('pk')
    if Patient.objects.get(pk=patient_id).owner.id != request.user.id:
        return redirect('/cinderella/')
    number = kwargs.get('int')
    context = {
        'medical_images': medical_images
    }
    print("entra no post2", patient_id, number)
    img_to_process = get_object_or_404(
        ImagesPatient, pk=patient_id, number=number)
    #img = Image.open(img_to_process.image.path)
    img = cv2.imread(img_to_process.image.path)
    print(img.shape)
    start_time = time.time()
    now = time.time()
    print('START:', now)
    kpts = keypoint_prediction(img)

    # print(kpts)
    # scheduler.run()
    print("--- %s seconds ---" % (time.time() - start_time))
    save_kpts(patient_id, number, kpts)

    #response = HttpResponseRedirect('bcctcore/')
    # return response
    # bcctcore(request)
    return render(request, 'bcctapp/medical_image_modal.html', context)


@login_required
def bcctcore(request, **kwargs):
    print("entra aqui bcctcore")
    # storage = get_messages(request)
    # storage = list(storage)
    image_pk = request.session['image_pk']
    name = request.session['name']
    print(name)
    incisura_jugularis_x = float(request.session['incisura_jugularis_x'])
    incisura_jugularis_y = float(request.session['incisura_jugularis_y'])
    left_nipple_x = float(request.session['left_nipple_x'])
    left_nipple_y = float(request.session['left_nipple_y'])
    right_nipple_x = float(request.session['right_nipple_x'])
    right_nipple_y = float(request.session['right_nipple_y'])
    left_endpoint_x = float(request.session['truth_lp_x'])
    left_endpoint_y = float(request.session['truth_lp_y'])
    left_midpoint_x = float(request.session['truth_midl_x'])
    left_midpoint_y = float(request.session['truth_midl_y'])
    right_midpoint_x = float(request.session['truth_midr_x'])
    right_midpoint_y = float(request.session['truth_midr_y'])
    right_endpoint_x = float(request.session['truth_rp_x'])
    right_endpoint_y = float(request.session['truth_rp_y'])
    # Right Breast Contour
    l_breast_contour_1_x = float(request.session['l_breast_contour_1_x'])
    l_breast_contour_1_y = float(request.session['l_breast_contour_1_y'])
    l_breast_contour_2_x = float(request.session['l_breast_contour_2_x'])
    l_breast_contour_2_y = float(request.session['l_breast_contour_2_y'])
    l_breast_contour_3_x = float(request.session['l_breast_contour_3_x'])
    l_breast_contour_3_y = float(request.session['l_breast_contour_3_y'])
    l_breast_contour_4_x = float(request.session['l_breast_contour_4_x'])
    l_breast_contour_4_y = float(request.session['l_breast_contour_4_y'])
    l_breast_contour_5_x = float(request.session['l_breast_contour_5_x'])
    l_breast_contour_5_y = float(request.session['l_breast_contour_5_y'])
    l_breast_contour_6_x = float(request.session['l_breast_contour_6_x'])
    l_breast_contour_6_y = float(request.session['l_breast_contour_6_y'])
    l_breast_contour_7_x = float(request.session['l_breast_contour_7_x'])
    l_breast_contour_7_y = float(request.session['l_breast_contour_7_y'])
    l_breast_contour_8_x = float(request.session['l_breast_contour_8_x'])
    l_breast_contour_8_y = float(request.session['l_breast_contour_8_y'])
    l_breast_contour_9_x = float(request.session['l_breast_contour_9_x'])
    l_breast_contour_9_y = float(request.session['l_breast_contour_9_y'])
    l_breast_contour_10_x = float(request.session['l_breast_contour_10_x'])
    l_breast_contour_10_y = float(request.session['l_breast_contour_10_y'])
    l_breast_contour_11_x = float(request.session['l_breast_contour_11_x'])
    l_breast_contour_11_y = float(request.session['l_breast_contour_11_y'])
    l_breast_contour_12_x = float(request.session['l_breast_contour_12_x'])
    l_breast_contour_12_y = float(request.session['l_breast_contour_12_y'])
    l_breast_contour_13_x = float(request.session['l_breast_contour_13_x'])
    l_breast_contour_13_y = float(request.session['l_breast_contour_13_y'])
    l_breast_contour_14_x = float(request.session['l_breast_contour_14_x'])
    l_breast_contour_14_y = float(request.session['l_breast_contour_14_y'])
    l_breast_contour_15_x = float(request.session['l_breast_contour_15_x'])
    l_breast_contour_15_y = float(request.session['l_breast_contour_15_y'])
    # Left Breast Contour
    r_breast_contour_1_x = float(request.session['r_breast_contour_1_x'])
    r_breast_contour_1_y = float(request.session['r_breast_contour_1_y'])
    r_breast_contour_2_x = float(request.session['r_breast_contour_2_x'])
    r_breast_contour_2_y = float(request.session['r_breast_contour_2_y'])
    r_breast_contour_3_x = float(request.session['r_breast_contour_3_x'])
    r_breast_contour_3_y = float(request.session['r_breast_contour_3_y'])
    r_breast_contour_4_x = float(request.session['r_breast_contour_4_x'])
    r_breast_contour_4_y = float(request.session['r_breast_contour_4_y'])
    r_breast_contour_5_x = float(request.session['r_breast_contour_5_x'])
    r_breast_contour_5_y = float(request.session['r_breast_contour_5_y'])
    r_breast_contour_6_x = float(request.session['r_breast_contour_6_x'])
    r_breast_contour_6_y = float(request.session['r_breast_contour_6_y'])
    r_breast_contour_7_x = float(request.session['r_breast_contour_7_x'])
    r_breast_contour_7_y = float(request.session['r_breast_contour_7_y'])
    r_breast_contour_8_x = float(request.session['r_breast_contour_8_x'])
    r_breast_contour_8_y = float(request.session['r_breast_contour_8_y'])
    r_breast_contour_9_x = float(request.session['r_breast_contour_9_x'])
    r_breast_contour_9_y = float(request.session['r_breast_contour_9_y'])
    r_breast_contour_10_x = float(request.session['r_breast_contour_10_x'])
    r_breast_contour_10_y = float(request.session['r_breast_contour_10_y'])
    r_breast_contour_11_x = float(request.session['r_breast_contour_11_x'])
    r_breast_contour_11_y = float(request.session['r_breast_contour_11_y'])
    r_breast_contour_12_x = float(request.session['r_breast_contour_12_x'])
    r_breast_contour_12_y = float(request.session['r_breast_contour_12_y'])
    r_breast_contour_13_x = float(request.session['r_breast_contour_13_x'])
    r_breast_contour_13_y = float(request.session['r_breast_contour_13_y'])
    r_breast_contour_14_x = float(request.session['r_breast_contour_14_x'])
    r_breast_contour_14_y = float(request.session['r_breast_contour_14_y'])
    r_breast_contour_15_x = float(request.session['r_breast_contour_15_x'])
    r_breast_contour_15_y = float(request.session['r_breast_contour_15_y'])
    print("r_breast_contour_15_y", r_breast_contour_15_y)
    context = {
        'image_pk': image_pk,
        'name': name,
        'incisura_jugularis_x': incisura_jugularis_x,
        'incisura_jugularis_y': incisura_jugularis_y,
        'left_nipple_x': left_nipple_x,
        'left_nipple_y': left_nipple_y,
        'right_nipple_x': right_nipple_x,
        'right_nipple_y': right_nipple_y,
        'left_endpoint_x': left_endpoint_x,
        'left_endpoint_y': left_endpoint_y,
        'left_midpoint_x': left_midpoint_x,
        'left_midpoint_y': left_midpoint_y,
        'right_midpoint_x': right_midpoint_x,
        'right_midpoint_y': right_midpoint_y,
        'right_endpoint_x': right_endpoint_x,
        'right_endpoint_y': right_endpoint_y,
        'l_breast_contour_1_x': l_breast_contour_1_x,
        'l_breast_contour_1_y': l_breast_contour_1_y,
        'l_breast_contour_2_x': l_breast_contour_2_x,
        'l_breast_contour_2_y': l_breast_contour_2_y,
        'l_breast_contour_3_x': l_breast_contour_3_x,
        'l_breast_contour_3_y': l_breast_contour_3_y,
        'l_breast_contour_4_x': l_breast_contour_4_x,
        'l_breast_contour_4_y': l_breast_contour_4_y,
        'l_breast_contour_5_x': l_breast_contour_5_x,
        'l_breast_contour_5_y': l_breast_contour_5_y,
        'l_breast_contour_6_x': l_breast_contour_6_x,
        'l_breast_contour_6_y': l_breast_contour_6_y,
        'l_breast_contour_7_x': l_breast_contour_7_x,
        'l_breast_contour_7_y': l_breast_contour_7_y,
        'l_breast_contour_8_x': l_breast_contour_8_x,
        'l_breast_contour_8_y': l_breast_contour_8_y,
        'l_breast_contour_9_x': l_breast_contour_9_x,
        'l_breast_contour_9_y': l_breast_contour_9_y,
        'l_breast_contour_10_x': l_breast_contour_10_x,
        'l_breast_contour_10_y': l_breast_contour_10_y,
        'l_breast_contour_11_x': l_breast_contour_11_x,
        'l_breast_contour_11_y': l_breast_contour_11_y,
        'l_breast_contour_12_x': l_breast_contour_12_x,
        'l_breast_contour_12_y': l_breast_contour_12_y,
        'l_breast_contour_13_x': l_breast_contour_13_x,
        'l_breast_contour_13_y': l_breast_contour_13_y,
        'l_breast_contour_14_x': l_breast_contour_14_x,
        'l_breast_contour_14_y': l_breast_contour_14_y,
        'l_breast_contour_15_x': l_breast_contour_15_x,
        'l_breast_contour_15_y': l_breast_contour_15_y,
        'r_breast_contour_1_x': r_breast_contour_1_x,
        'r_breast_contour_1_y': r_breast_contour_1_y,
        'r_breast_contour_2_x': r_breast_contour_2_x,
        'r_breast_contour_2_y': r_breast_contour_2_y,
        'r_breast_contour_3_x': r_breast_contour_3_x,
        'r_breast_contour_3_y': r_breast_contour_3_y,
        'r_breast_contour_4_x': r_breast_contour_4_x,
        'r_breast_contour_4_y': r_breast_contour_4_y,
        'r_breast_contour_5_x': r_breast_contour_5_x,
        'r_breast_contour_5_y': r_breast_contour_5_y,
        'r_breast_contour_6_x': r_breast_contour_6_x,
        'r_breast_contour_6_y': r_breast_contour_6_y,
        'r_breast_contour_7_x': r_breast_contour_7_x,
        'r_breast_contour_7_y': r_breast_contour_7_y,
        'r_breast_contour_8_x': r_breast_contour_8_x,
        'r_breast_contour_8_y': r_breast_contour_8_y,
        'r_breast_contour_9_x': r_breast_contour_9_x,
        'r_breast_contour_9_y': r_breast_contour_9_y,
        'r_breast_contour_10_x': r_breast_contour_10_x,
        'r_breast_contour_10_y': r_breast_contour_10_y,
        'r_breast_contour_11_x': r_breast_contour_11_x,
        'r_breast_contour_11_y': r_breast_contour_11_y,
        'r_breast_contour_12_x': r_breast_contour_12_x,
        'r_breast_contour_12_y': r_breast_contour_12_y,
        'r_breast_contour_13_x': r_breast_contour_13_x,
        'r_breast_contour_13_y': r_breast_contour_13_y,
        'r_breast_contour_14_x': r_breast_contour_14_x,
        'r_breast_contour_14_y': r_breast_contour_14_y,
        'r_breast_contour_15_x': r_breast_contour_15_x,
        'r_breast_contour_15_y': r_breast_contour_15_y
    }

    # return render(request, 'general/other_view.html', {'name:name})
    return render(request, 'bcctapp/bcctCore.html', context)


def update_breast_bra(request, **kwargs):
    if request.method == 'POST':
        if 'BRA' in request.POST and 'image_pk' in request.POST:
            print("kwargs", kwargs)
            braValue = request.POST['BRA']
            imgID = request.POST['image_pk']
            print(braValue, imgID)
            #patient = get_object_or_404(Patient, pk=imgID)
            Patient.objects.filter(pk=imgID).update(bra=braValue)
            #patient.bra = str(braValue)
            #print("patient bra ",patient.bra)
        return HttpResponse('Success!')
    return HttpResponse('FAIL!')


# contact form view
def contact(request):
    if request.method == 'POST':
        form = ContactForm(data = request.POST)

        if form.is_valid():

            message_name = request.POST.get('name')
            message_email = request.POST.get('email')

            content = 'Name: ' + message_name + '\nEmail: ' + message_email + '\nContent: ' + \
                request.POST.get('content') + '\nScore: ' + \
                request.POST.get('score')

            send_mail(
                'You got new feedback from ' + message_name,  # subject
                content,  # message
                message_email,  # from email
                [settings.EMAIL_HOST_USER],
            )

        return redirect('/')
    else :
        if request.user.is_authenticated :
            form = ContactForm(initial = {'email': request.user.email, 'name': request.user.username})
        else :
            form = ContactForm()
        return render(request, 'bcctapp/contact.html',  {'form': form})

# interactions


# chat

def chat(request):
    return render(request, 'bcctapp/chat.html')
