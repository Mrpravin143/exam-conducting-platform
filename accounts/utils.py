import random
from django.core.mail import EmailMessage

def send_registration_email(user, otp):
    """
    Sends enrollment number, role, OTP and candidate image (if available) to the user's email.
    """
    subject = "Your Registration Details + OTP"
    body = f"""
Hello {user.username},

🎉 Registration Successful!

✅ Enrollment Number: {user.enrollment_number}
✅ Role: {user.role}

Please verify your OTP: {otp} (valid for 5 minutes)

Regards,
Admin Team
    """

    email_message = EmailMessage(
        subject,
        body,
        "pravinsaindane2005@gmail.com",   # sender
        [user.email],             # recipient
    )

    # Attach candidate image if uploaded
    if user.candidate_image:
        email_message.attach_file(user.candidate_image.path)

    email_message.send(fail_silently=False)