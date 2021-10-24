from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # User Management 
    path('accounts/', include("allauth.urls")),

    # Local Apps
    path("teachers/", include("teachers.urls", namespace="teachers")),
    path("support/", include("supports.urls", namespace="support")),
    path("", include("homeapp.urls", namespace="home")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
