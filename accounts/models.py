from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings



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

    USERNAME_FIELD = 'enrollment_number'  
    REQUIRED_FIELDS = ['username', 'email']


    def save(self, *args, **kwargs):
        if self.role == "student" and not self.enrollment_number:
            prefix = "SEN"

            last_student = User.objects.filter(role="student", enrollment_number__startswith=prefix).order_by("-id").first()
            if last_student and last_student.enrollment_number:
                try:
                    last_serial = int(last_student.enrollment_number.replace(prefix, "")) 
                except:
                    last_serial = 0
            else:
                last_serial = 0

            new_serial = last_serial + 1

            self.enrollment_number = f"{prefix}{new_serial:06d}"

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.username} ({self.role})"



