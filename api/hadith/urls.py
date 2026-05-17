from django.urls import path

from hadith.views import HadithSabrListCreateView

urlpatterns = [
    path("sabr/", HadithSabrListCreateView.as_view(), name="hadith-sabr"),
]
