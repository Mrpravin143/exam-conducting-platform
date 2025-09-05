from django.urls import path
from accounts.views import *

urlpatterns = [
    path('register/',register_view,name='register'),
    path('otp_verify/',otp_verify_view, name='otp_verify'),
    path('login/',login_view,name='login'),
    path('logout/',logout_view,name='logout'),
    path('registration_success/',registration_success,name='registration_success'),
    
]