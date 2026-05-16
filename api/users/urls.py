from django.urls import path

from users.views import ChangePasswordView, CurrentUserView, UserCreateView

urlpatterns = [
    path("users/", UserCreateView.as_view(), name="user-create"),
    path("users/me/", CurrentUserView.as_view(), name="user-me"),
    path("users/me/change-password/", ChangePasswordView.as_view(), name="user-change-password"),
]
