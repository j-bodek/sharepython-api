"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView

urlpatterns = [
    path(
        "",
        SpectacularSwaggerView.as_view(url_name="api_schema"),
        name="api_docs",
    ),  # docs
    path("schema/", SpectacularAPIView.as_view(), name="api_schema"),
    path("admin/", admin.site.urls),
    path("auth/", include("jwt_auth.urls")),  # auth endpoints
    path("", include("users.urls")),  # users endpoints
    path("", include("codespace.urls")),  # codespace endpoints
    path("", include("reset_password.urls")),  # reset password endpoints
]
