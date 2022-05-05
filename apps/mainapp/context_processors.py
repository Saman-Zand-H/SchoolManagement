from django.conf import settings


def vapid_key(request):
    return{"vapid_key": getattr(
        settings, "WEBPUSH_SETTINGS", {}).get("VAPID_PUBLIC_KEY")}
