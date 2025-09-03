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
        candidate_image = request.FILES.get('candidate_image')

        # Validations
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
            password=make_password(password1),
            candidate_image=candidate_image
        )
        user.save()  # enrollment_number auto generate 

        context = {
            "enrollment_number": user.enrollment_number,
            "username": user.username,
            "candidate_image_url": user.candidate_image.url if user.candidate_image else None,
        }
        return render(request, "registration_success.html", context)

    return render(request, "register.html")



def login_view(request):
    if request.method == "POST":
        enrollment_number = request.POST.get('enrollment_number', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, enrollment_number=enrollment_number, password=password)
        if user:
            login(request, user)
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'student':
                return redirect('student_dashboard')

        messages.error(request, "Invalid Enrollment Number or Password.")
    return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def registration_success(request):
    return render(request,'registration_success.html')