from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import User   
from django.core.mail import send_mail
import random
from accounts.utils import send_registration_email
from django.utils import timezone


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

        # User create
        user = User(
            username=username,
            email=email,
            role=role,
            password=make_password(password1),
            candidate_image=candidate_image
        )
        user.save()  # enrollment_number auto generate 


        # Generate OTP
        otp = f"{random.randint(100000, 999999)}"
        user.set_otp(otp)
       

        # Send email + OTP
        if email:
            send_registration_email(user, otp)

        # Save user id in session
        request.session["user_id"] = user.id  

        return redirect("otp_verify")  # OTP verify page
        
    return render(request, "register.html")


def otp_verify_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("register")

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        entered_otp = request.POST.get("otp", "").strip()
        if user.verify_otp(entered_otp):
            user.is_verified = True
            user.otp = None
            user.otp_created_at = None
            user.save()
            del request.session["user_id"]
            return render(request, "registration_success.html", {
                "enrollment_number": user.enrollment_number,
                "username": user.username,
                "candidate_image_url": user.candidate_image.url if user.candidate_image else None
            })
        else:
            messages.error(request, "Invalid OTP or OTP expired. Please try again.")

    return render(request, "otp_verify.html")




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