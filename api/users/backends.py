from django.contrib.auth.backends import ModelBackend
from .models import CustomUser

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get('email', username)
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None
