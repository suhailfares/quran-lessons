from django.urls import path

from quran.views import (
    StudentHifzListCreateView,
    StudentHifzDetailView,
    QuranSabrListCreateView,
)

urlpatterns = [
    path("hifz/", StudentHifzListCreateView.as_view(), name="student-hifz"),
    path("hifz/<int:pk>/", StudentHifzDetailView.as_view(), name="student-hifz-detail"),
    path("sabr/", QuranSabrListCreateView.as_view(), name="quran-sabr"),
]
