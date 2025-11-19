from django.urls import path

from lessons.views import LessonView

urlpatterns = [
    path("lessons/", LessonView.as_view(), name="lessons")
]