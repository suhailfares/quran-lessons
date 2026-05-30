from django.urls import path
from rest_framework.routers import DefaultRouter

from .report import ReportView
from .views import StudentViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')

# ReportView must come before router.urls so 'report' isn't matched as a student pk.
urlpatterns = [
    path("students/report/", ReportView.as_view(), name="student-report"),
] + router.urls