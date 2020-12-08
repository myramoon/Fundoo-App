from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from rest_framework.viewsets import ModelViewSet
from .serializers import AccountDetailSerializer
from .models import Account
from django.contrib.auth import login
from django.urls import reverse
from api.forms import CustomUserCreationForm
from rest_framework.permissions import IsAuthenticated

# views

class AccountView(ModelViewSet):
    permission_classes = (IsAuthenticated,)

    queryset = Account.objects.all()
    serializer_class = AccountDetailSerializer

def dashboard(request):
    return render(request , "users/dashboard.html")   

def register(request):
    if request.method == "GET":
        return render(
            request, "users/register.html",
            {"form": CustomUserCreationForm}
        )  
    elif request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request , user)
            return redirect(reverse("dashboard"))
        else:
            return HttpResponse("Improper form details")    
        