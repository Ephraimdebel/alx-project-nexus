"""
URL configuration for polls_backend project.

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
# from django.contrib import admin
# from django.urls import path,include

# urlpatterns = [
#     path('admin/', admin.site.urls),
#      path("api/", include("poll.urls")),   # <--- REST API root
#     path("", include("rest_framework.urls")),  # optional: browsable login
# ]


# project/urls.py (add)
from django.urls import path, include
from django.contrib import admin
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import JsonResponse
from django.contrib.auth.models import User

schema_view = get_schema_view(
   openapi.Info(
      title="Polls API",
      default_version='v1',
      description="API docs for Polls backend",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
def create_superuser(request):
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@example.com", "AdminPassword123")
        return JsonResponse({"status": "superuser created"})
    return JsonResponse({"status": "superuser already exists"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('poll.urls')),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path("create-superuser/", create_superuser),
]
