from quran.views import StudentHifzCreateView
from django.urls import path

urlpatterns = [
    path("hifz/", StudentHifzCreateView.as_view(), name="student-hifz-create"),
]