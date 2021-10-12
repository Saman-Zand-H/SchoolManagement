from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # User Management 
    path('accounts/', include("allauth.urls")),
    path("dashboard/", include("teachers.urls", namespace="teachers")),
    path("", include("homeapp.urls", namespace="home")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
