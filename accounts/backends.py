from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib import admin
from accounts.models import User

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Try to fetch user by email
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            try:
                # Try to fetch user by username
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                return None
        if user.check_password(password):  # Check the password
            return user
        return None

