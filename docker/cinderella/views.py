from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import CinderellaImages
from .forms import CinderellaImagesForm

# Create your views here.
@login_required
def home_cinderella(request):

    context = {
        'title':'Cinderella Project'
    }

    if request.method == 'POST':
        if 'password' in request.POST:
            pwd = request.POST.get('password', None)

            if pwd == 'champalimaud':
                
                response = HttpResponseRedirect('cinderella_url/')
                return response
    
    return render(request, 'cinderella/cinderella_project.html', context)

@login_required
def cinderella_url(request):

    context ={
        'title':'Cinderella Application Demo'
    }

    if request.method == 'POST':
        if 'age' and 'weight' and 'height' in request.POST:
            age = request.POST.get('age', None)
            weight = request.POST.get('weight', None)
            height = request.POST.get('height', None)

            # Load range values
            age_range = request.POST.get('yrRange', None)
            weight_range = request.POST.get('wgtRange', None)
            height_range = request.POST.get('hgtRange', None)



            # Save into request.session[]

            request.session['age'] = str(age)
            request.session['weight'] = str(weight)
            request.session['height'] = str(height)
            request.session['age_range'] = str(age_range)
            request.session['weight_range'] = str(weight_range)
            request.session['height_range'] = str(height_range)

            response = HttpResponseRedirect('cinderella_results/')
            return response



    return render(request, 'cinderella/cinderella_application.html', context)


@login_required
def cinderella_results(request):

    # Obtain variables from request.session
    age = int(request.session['age'])
    weight = int(request.session['weight'])
    height = int(request.session['height'])

    age_range = int(request.session['age_range'])
    weight_range = int(request.session['weight_range'])
    height_range = int(request.session['height_range'])

    cinderella_images = CinderellaImages.objects.all()

    # Filter according to a distribution
    age_lims = [a for a in range(age-age_range, age+age_range+1)]
    weight_lims = [w for w in range(weight-weight_range, weight+weight_range+1)]
    height_lims = [h for h in range(height-height_range, height+height_range+1)]

    # Create empty results list

    results = []
    for item in cinderella_images:
        if (item.age>=age_lims[0] and item.age<age_lims[-1]) \
            and (item.weight>=weight_lims[0] and item.weight<weight_lims[-1]) \
                and (item.height>=height_lims[0] and item.height<height_lims[-1]):
                
                results.append(item)


    context = {
        'age':age,
        'age_lims':age_range,
        'weight':weight,
        'weight_lims':weight_range,
        'height':height,
        'height_lims':height_range,
        'cinderella_images':cinderella_images,
        'results':results
    }


    if request.method=='POST':
        if 'check_clinical_study' in request.POST:
            study_id = request.POST.get('check_clinical_study', None)
            request.session['study_id'] = str(study_id)

            response = HttpResponseRedirect('clinical_study/')
            return response


    return render(request, 'cinderella/cinderella_application_results.html', context)


#File Upload Function
@login_required
def upload_cinderella_images(request):
    if request.method == 'POST':
        form = CinderellaImagesForm(request.POST, request.FILES)
        form.instance.doctor = request.user
        if form.is_valid():
            form.save()
            return redirect('cinderella_url')
    else:
        form = CinderellaImagesForm()
    context = {
        'form':form
    }
    return render(request, 'cinderella/upload_cinderella_images.html', context)

# View: "Check Clinical Study"
@login_required
def check_clinical_study(request):

    # You get the Study ID from submitted form
    study_id = int(request.session['study_id'])

    # Query the DB
    query = CinderellaImages.objects.filter(id=study_id)

    # query is a list w/ one element, so we have to retrieve index==0
    obj = query[0]

    context = {
        'obj':obj,
        'study_id':study_id
    }



    return render(request, 'cinderella/p', context)