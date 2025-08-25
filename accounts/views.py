from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import User

# Create your views here.
def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        role = request.POST.get('role', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        # Basic validations
        if not username or not role or not password1 or not password2:
            messages.error(request, "All fields are required.")
            return render(request, "register.html")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, "register.html")

        user = User(
            username=username,
            email=email,
            role=role,
            password=make_password(password1)
        )
        user.save()
        messages.success(request, "Registration successful. Please login.")
        return redirect('login')

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # Role-based redirect
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'student':
                return redirect('student_dashboard')
                
        messages.error(request, "Invalid credentials.")
    return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')