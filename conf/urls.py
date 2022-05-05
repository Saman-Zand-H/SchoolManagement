from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.templatetags.static import static as static_file
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler403, handler500
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Takhte Whiteboard API",
        description="A web app for managing the chores of your school.",
        default_version="v1",
        contact=openapi.Contact(name="Saman Zand", email="tnsperuse@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    # Notifications
    path(
        route="webpush/",
        view=include("webpush.urls"),
    ),
    
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
    path(
        route="api/docs/",
        view=schema_view.with_ui(
            "redoc",
        ),
        name="schema-redoc",
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
    path(
        route="main/",
        view=include("mainapp.urls", namespace="main"),
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
