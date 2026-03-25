from django.urls import path

from lessons.views import LessonView, AttendanceView

urlpatterns = [
    path("lessons/", LessonView.as_view(), name="lessons"),
    path("lessons/attendances", AttendanceView.as_view(), name="attendances"),
    path("lessons/<int:lesson_id>/attendances", AttendanceView.as_view(), name="lesson-attendances"),
]
