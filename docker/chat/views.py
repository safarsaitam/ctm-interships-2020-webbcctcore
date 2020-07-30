from django.shortcuts import render, redirect
from .models import Group, Message
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib.auth.models import User







def index(request):
    return render(request, 'chat/index.html')


def ShowChatPage(request, room_name):

    user_id = str(request.user.id)
    teams = []
    for group in Group.objects.all():
        users = group.team.users.split()
        if user_id in users:
            teams.append(group.team.id)

    if room_name is None:
        return render(request, 'chat/room.html', {
         'groups': Group.objects.filter(team__in=teams)
        })

    elif Group.objects.filter(pk=room_name).exists():
        return render(request, 'chat/room.html', {
        'group': Group.objects.filter(pk=room_name).first(),
        'pk': room_name,
        'groups': Group.objects.filter(team__in=teams),
        'messages' : Message.objects.filter(group=room_name).order_by('timestamp')[:15]
        })
    else:
        return redirect('/')


def loadMessage(request):
    if request.is_ajax and request.method == "POST":
        const_load = 15
        group_id = request.POST.get('group_id', None)
        number_messages = int(request.POST.get('page')) * const_load

        if Message.objects.filter(group=group_id).exists():
            data =  Message.objects.order_by('-timestamp').all()[number_messages:number_messages + const_load]
            users = {}

            for info in data:
                users[str(info.author.id)]  = {
                    'id':info.author.id,
                    'username' : info.author.username,
                    'image': info.author.profile.image.url 
                }
            
            load_more = True
            
            if data.count() < const_load:
                load_more = False

            return JsonResponse({"messages" : list(data.values()), 'users': users, 'load_more' : load_more}, status = 200)
        else:
            return JsonResponse({}, status = 400)
    return JsonResponse({}, status = 400)


class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    fields = '__all__'

    def form_valid(self, form):
        #check if team valid
        print(self)
        return super().form_valid(form)

class GroupUpdateView(LoginRequiredMixin, UpdateView):
    model = Group
    fields = ['name']

    def form_valid(self, form):
        #check if team valid
        #print(self)
        return super().form_valid(form)