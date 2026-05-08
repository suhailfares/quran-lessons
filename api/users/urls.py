from django.urls import path

from users.views import UserCreateView, CurrentUserView

urlpatterns = [
    path("users/", UserCreateView.as_view(), name="user-create"),
    path("users/me/", CurrentUserView.as_view(), name="user-me"),
]
