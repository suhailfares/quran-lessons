"""
URL configuration for quranlessons project.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from users.jwt import VersionedTokenObtainPairView, VersionedTokenRefreshView

urlpatterns = [
    # OpenAPI schema in JSON
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger_ui"),
    # ReDoc UI
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('students.urls')),
    path('api/quran/', include('quran.urls')),
    path('api/hadith/', include('hadith.urls')),
    path('api/', include('lessons.urls')),
    path("api/auth/login/", VersionedTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/login/refresh/", VersionedTokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include("habits.urls")),
]
