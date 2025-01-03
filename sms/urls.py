from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from django.conf import settings
from django.conf.urls.static import static
# Adding JWT security definition
schema_view = get_schema_view(
    openapi.Info(
        title="School Management System API",
        default_version='v1',
        description="API documentation for this project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny, ),
    # Adding security definitions for Bearer token
    authentication_classes=[],  # Keep this empty for swagger view
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apis.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
