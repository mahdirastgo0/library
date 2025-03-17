from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model
from .tokens import account_activation_token
from itsdangerous import URLSafeTimedSerializer
from django.conf import settings

User = get_user_model()


def activateEmail(request, user, to_email):
    subject = "Activate Your Account"
    current_site = get_current_site(request)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    activation_link = f"http://{current_site.domain}{reverse('activate', kwargs={'uidb64': uid, 'token': token})}"

    message = render_to_string('accounts/activation_account.html', {
        'user': user,
        'activation_link': activation_link
    })

    plain_message = strip_tags(message)

    send_mail(subject, plain_message, 'rastgoom23@gmail.com', [to_email], html_message=message)



def generate_token(email):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt='email-verification')

def verify_token(token, max_age=3600):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        email = serializer.loads(token, salt='email-verification', max_age=max_age)
        return email
    except Exception:
        return None

def send_verification_email(user):
    subject = "Verify Your Email"
    token = generate_token(user.email)  # Generate the token
    verification_url = f"{settings.DOMAIN}/accounts/verify-email/{token}/"  # Use the DOMAIN setting
    html_message = render_to_string('accounts/verification_email.html', {'verification_url': verification_url})
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_message)