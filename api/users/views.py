from rest_framework import generics
from rest_framework.response import Response
from .models import CustomUser
from .serializers import UserSerializer

class ProfileDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = "username"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        profile = {
            "username": instance.username,
            "bio": instance.bio,
            "image": instance.image,
        }
        return Response({"profile": profile})
