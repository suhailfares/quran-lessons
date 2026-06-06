from django.urls import path

from users.views import AdminCreateView, ChangePasswordView, CurrentUserView, ManagerCreateView, MosqueListView, UserCreateView, UserDeleteView, UserListView

urlpatterns = [
    path("mosques/", MosqueListView.as_view(), name="mosque-list"),
    path("users/", UserCreateView.as_view(), name="user-create"),
    path("users/admins/", AdminCreateView.as_view(), name="admin-create"),
    path("users/managers/", ManagerCreateView.as_view(), name="manager-create"),
    path("users/all/", UserListView.as_view(), name="user-list"),
    path("users/me/", CurrentUserView.as_view(), name="user-me"),
    path("users/me/change-password/", ChangePasswordView.as_view(), name="user-change-password"),
    path("users/<str:username>/", UserDeleteView.as_view(), name="user-delete"),
]
