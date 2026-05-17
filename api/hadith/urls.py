from django.urls import path

from hadith.views import (
    HadithSabrListCreateView,
    HadithHifzListCreateView,
    HadithHifzDetailView,
)

urlpatterns = [
    path("sabr/", HadithSabrListCreateView.as_view(), name="hadith-sabr"),
    path("hifz/", HadithHifzListCreateView.as_view(), name="hadith-hifz"),
    path("hifz/<int:pk>/", HadithHifzDetailView.as_view(), name="hadith-hifz-detail"),
]
