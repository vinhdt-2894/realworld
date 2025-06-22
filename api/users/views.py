from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken

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

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data.get('user', request.data))
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": {
                "username": user.username,
                "email": user.email,
                "bio": user.bio,
                "image": user.image,
                "token": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data.get('user', request.data))
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": {
                "username": user.username,
                "email": user.email,
                "bio": user.bio,
                "image": user.image,
                "token": str(refresh.access_token),
            }
        })

class UserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        print("Retrieving user details")
        serializer = self.get_serializer(self.get_object())
        return Response({"user": serializer.data})

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data.get('user', request.data), partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"user": serializer.data})
