from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from .models import UserProfile


def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data['username'],password=form.cleaned_data['password'])
            UserProfile.objects.create(user=user,role=form.cleaned_data['role'])
            messages.success(request, "User registered successfully")
            return redirect('register_user')
    else:
        form = RegisterForm()
    return render(request,'registration/register.html',{'form': form})


def login_user(request):
    if request.method == 'POST':
        errors = []
        if not request.POST.get("username"):
            errors.append("Username is required.")
        if not request.POST.get("password"):
            errors.append("Password is required.")
        if errors:
            return render(request, "registration/login.html", {"errors": errors})
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request, user)
            profile = UserProfile.objects.get(user=user)
            if profile.role == 'admin':
                return redirect('admin_dashboard')
            elif profile.role == 'sales_manager':
                return redirect('sales_dashboard')
            elif profile.role == 'stock_attendant':
                return redirect('stock_dashboard')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'registration/login.html')


def logout_user(request):
    logout(request)
    return redirect('login')