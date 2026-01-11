"""
URL configuration for quranlessons project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
import rest_framework_simplejwt.views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

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
    path('api/', include('lessons.urls')),
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include("habits.urls")), 
]

