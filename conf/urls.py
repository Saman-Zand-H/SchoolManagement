from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler403, handler500

urlpatterns = [
    # Admin
    path('emperor-page/', admin.site.urls),

    path('i18n/', include('django.conf.urls.i18n')),

    # User Management 
    path('accounts/', include("allauth.urls")),
    path('users/', include("users.urls")),

    # Local Apps
    path("teacher/", include("teachers.urls", namespace="teachers")),
    path("support/", include("supports.urls", namespace="supports")),
    path("", include("homeapp.urls", namespace="home")),
    path('ckeditor/', include('ckeditor_uploader.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))

# Custom error pages
handler404 = "apps.mainapp.utils.not_found_error"
handler403 = "apps.mainapp.utils.forbidden_error"
handler500 = "apps.mainapp.utils.internal_error"
