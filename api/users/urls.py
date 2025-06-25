from django.urls import path
from .views import RegisterView, LoginView, UserRetrieveUpdateView, ProfileDetailView, ProfileFollowView

urlpatterns = [
    path("users/", RegisterView.as_view(), name="user-register"),
    path("users/login/", LoginView.as_view(), name="user-login"),
    path("user/", UserRetrieveUpdateView.as_view(), name="user-detail"),
    path("profiles/<str:username>/", ProfileDetailView.as_view(), name="profile-detail"),
    path("profiles/<str:username>/follow/", ProfileFollowView.as_view(), name="profile-follow"),
]
