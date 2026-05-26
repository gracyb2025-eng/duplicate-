from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

from .forms import RegisterForm
from .models import UserProfile


def register_user(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )

            UserProfile.objects.create(
                user=user,
                role=form.cleaned_data['role']
            )

            messages.success(request, "User registered successfully")

            return redirect('register_user')

    else:
        form = RegisterForm()

    return render(
        request,
        'registration/register.html',
        {'form': form}
    )
