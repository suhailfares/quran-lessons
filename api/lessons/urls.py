from django.urls import path
from rest_framework.routers import DefaultRouter

from lessons.views import LessonViewSet, AttendanceView


router = DefaultRouter()
router.register(r"lessons", LessonViewSet, basename="lesson")

urlpatterns = router.urls + [
    path("lessons/attendances", AttendanceView.as_view(), name="attendances"),
    path("lessons/<int:lesson_id>/attendances", AttendanceView.as_view(), name="lesson-attendances"),
]
