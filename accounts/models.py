from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import random
from django.core.mail import EmailMessage
import hashlib
from django.utils import timezone





# Create your models here.

class User(AbstractUser):
    # Define roles
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    enrollment_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    candidate_image = models.ImageField(upload_to='candidateimage/',blank=True, null=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'enrollment_number'  
    REQUIRED_FIELDS = ['username', 'email']


    def save(self, *args, **kwargs):
        if self.role == "student" and not self.enrollment_number:
            while True:
                random_number = f"{random.randint(100000, 999999)}"  # 100000 - 999999
                if not User.objects.filter(enrollment_number=random_number).exists():
                    self.enrollment_number = random_number
                    break

        super().save(*args, **kwargs)

    # OTP Verifications

    def set_otp(self, otp):
        self.otp = hashlib.sha256(otp.encode()).hexdigest()
        self.otp_created_at = timezone.now()
        self.save()

    def verify_otp(self, otp):
        # Check OTP expiry 5 minutes
        if not self.otp or not self.otp_created_at:
            return False
        if timezone.now() > self.otp_created_at + timezone.timedelta(minutes=5):
            return False
        return hashlib.sha256(otp.encode()).hexdigest() == self.otp


    def __str__(self):
        return f"{self.username} ({self.role})"



