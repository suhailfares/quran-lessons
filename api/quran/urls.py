from django.urls import path

from quran.views import StudentHifzListCreateView, StudentHifzDetailView

urlpatterns = [
    path("hifz/", StudentHifzListCreateView.as_view(), name="student-hifz"),
    path("hifz/<int:pk>/", StudentHifzDetailView.as_view(), name="student-hifz-detail"),
]
