from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler403, handler500
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Admin
    path(
        route='emperor-page/', 
        view=admin.site.urls,
    ),
    
    # Localization
    path(
        route='i18n/', 
        view=include('django.conf.urls.i18n'),
    ),

    # User Management 
    path(
        route='accounts/', 
        view=include("allauth.urls")),
    path(
        route='users/', 
        view=include("users.urls")),

    # API
    path(
        route='api/v1/', 
        view=include("api.urls", namespace="api"),
    ),
    path(
        route='api/v1/auth/',
        view=include('dj_rest_auth.urls'),        
    ),
    path(
        route='api/v1/auth/registration/',
        view=include("dj_rest_auth.registration.urls"),
    ),
    path(
        route="api-auth/",
        view=include("rest_framework.urls"),
    ),

    # Local Apps
    path(
        route='teacher/', 
        view=include("teachers.urls", namespace="teachers"),
    ),
    path(
        route='support/', 
        view=include("supports.urls", namespace="supports"),
    ),
    path(
        route='students/', 
        view=include("students.urls", namespace="students"),
    ),
    path(
        route='messenger/', 
        view=include("messenger.urls", namespace="messenger"),
    ),
    path(
        route='', 
        view=include("homeapp.urls", namespace="home"),
    ),
    path(
        route='ckeditor/', 
        view=include('ckeditor_uploader.urls'),
    ),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns.append(
        path(
            route="__debug__/", 
            view=include(debug_toolbar.urls),
        ),
    )

# Custom error pages
handler404 = "apps.mainapp.utils.not_found_error"
handler403 = "apps.mainapp.utils.forbidden_error"
handler500 = "apps.mainapp.utils.internal_error"
