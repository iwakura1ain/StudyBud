from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

from .models import Room, Topic, Message
from .forms import RoomForm, UserForm


# Create your views here.

#views practice

# rooms = [
#     {"id": 1, "name": "room1"},
#     {"id": 2, "name": "room2"},
#     {"id": 3, "name": "room3"},
#     {"id": 4, "name": "room4"}    
# ]


def HomeView(request, template_path="base/home.html"):
    if (q := request.GET.get("q")) is not None:
        room_view = Room.objects.filter(Q(topic__name__icontains=q)
                                        | Q(name__icontains=q)
                                        | Q(desc__icontains=q))
        room_count = room_view.count()

        room_messages = Message.objects.filter(Q(user__username__icontains=q)
                                               | Q(room__name__icontains=q)
                                               | Q(room__topic__name__icontains=q))

        topics = Topic.objects.filter(Q(name__icontains=q))
    else:
        room_view = Room.objects.all()
        room_count = room_view.count()
        room_messages = Message.objects.all()
        topics = Topic.objects.all()
        
    context = {
        "rooms": room_view,
        "room_count": room_count,
        "room_messages": room_messages,
        "topics": topics,
        "create-room": "create-room/",
        "update-room": "update-room/",
        "page_heading": "Home"
    }

    return render(request, template_path, context)


def TopicsView(request):
    return HomeView(request, "base/topics.html")


def ActivitiesView(request):
    return HomeView(request, "base/activities.html")


def LoginView(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            User.objects.get(username=username)
            user = authenticate(request, username=username, password=password)

            if(user is not None):
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Username or Password wrong...")
                return redirect("login_view")            

        except User.DoesNotExist:
            messages.error(request, "User does not exist...")
            return redirect("login_view")
            
    elif request.method == "GET":
        if request.user.is_authenticated:
            return redirect("home")
        else:
            context = {}
            return render(request, "base/login.html", context)
    
    
def LogoutView(request):
    logout(request)
    return redirect("home")


def RegisterView(request):
    if request.method == "POST":
        if (user_data := UserCreationForm(request.POST)).is_valid():
            user = user_data.save(commit=False)
            user.username = user.username.lower()
            user.save()

            login(request, user)
            return redirect("home")

        else:
            messages.error(request, "Error while registration...")
            return redirect("register_view")
        
    elif request.method == "GET":
        context = {"form": UserCreationForm()}
        return render(request, "base/register.html", context)

    
def ProfileView(request, key):
    user = User.objects.get(id=key)
    rooms = Room.objects.filter(Q(host=user))
    room_messages = Message.objects.filter(Q(user=user))
    topics = Topic.objects.all()

    context = {
        "user": user,
        "rooms": rooms,
        "room_messages": room_messages,
        "topics": topics,
        "page_heading": user.username        
    }
    
    return render(request, "base/profile.html", context)


def ProfileEditView(request, key):
    user = User.objects.get(id=key)
    if request.method == "GET":
        context = {"form": UserForm(instance=user)}
        return render(request, "base/edit_user.html", context)

    elif request.method == "POST":
        if (user_data := UserForm(request.POST, instance=user)).is_valid():
            user_data.save()
            return redirect("profile_view", key=user.id)
    
def RoomView(request, key):
    if request.method == "POST":
        if request.user.is_authenticated:
            messages = Message.objects.create(
                user=request.user,
                room=Room.objects.get(id=key),
                body=request.POST.get("body")            
            )
            Room.objects.get(id=key).participants.add(request.user)

            return redirect("room_view", key=key)

        else:
            return redirect("login_view")

    elif request.method == "GET":
        try:
            room = Room.objects.get(id=key)
            participants = room.participants.all()
            child_messages = room.message_set.all().order_by("-first_created")  # weird syntax

        except AttributeError:
            child_messages = []

        context = {
            "room": room,
            "child_messages": child_messages,
            "participants": participants
        }
        
        return render(request, "base/room.html", context)
    
@login_required(login_url="/login")
def RoomCreate(request): 
    if request.method == "POST":
        # if (data := RoomForm(request.POST)).is_valid():
        #     room = data.save(commit=False)
        #     room.host = request.user
        #     room.save()
        #     room.participants.add(request.user)
            
        #     return redirect("home")


        try:
            host = request.user
            name = request.POST.get("name")
            desc = request.POST.get("desc")
            topic = Topic.objects.get_or_create(name=request.POST.get("topic"))[0]

        except:
            messages.error(request, "Wrong Input...")
            return redirect("room_creation")


        new_room = Room.objects.create(
            host=host,
            name=name,
            desc=desc,
            topic=topic                
        )
        new_room.participants.add(request.user)
        return redirect("home")

    elif request.method == "GET":
        context = {"is_new": True, "topics": Topic.objects.all()}
        return render(request, "base/form.html", context)


@login_required(login_url="/login")
def RoomUpdate(request, key):
    room = Room.objects.get(id=key)

    if IsOwner(request, room):
        if request.method == "POST":
            try:
                room.name = request.POST.get("name")
                room.desc = request.POST.get("desc")
                room.topic = Topic.objects.get_or_create(name=request.POST.get("topic"))[0]
                room.save()
                
            except:
                messages.error(request, "Wrong Input...")
                return redirect("room_update", key=room.id)

            return redirect("room_view", key=room.id)

        elif request.method == "GET":
            context = {"is_new": False, "room_instance": room}
            return render(request, "base/form.html", context)
    else:
        return HttpResponse("Denied")

    
@login_required(login_url="/login")
def RoomDelete(request, key):
    room = Room.objects.get(id=key)

    if request.method == "POST":
        room.delete()
        return redirect("home")
    
    elif request.method == "GET":
        context = {"obj": room}        
        return render(request, "base/delete.html", context)
    
    
def MessageDelete(request, key):
    if (msg := Message.objects.get(id=key)).user == request.user:
        msg.delete()
        
    else:
        messages.error(request, "Denied")

    return redirect("home")
        
    
def IsOwner(request, room):
    if request.user == room.host:
        return True
    else:
        return False
    










