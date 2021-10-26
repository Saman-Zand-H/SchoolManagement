from django.shortcuts import render


def not_found_error(request, exception):
    data = {}
    return render(request, "errors/404.html", data, status=404)


def forbidden_error(request, exception):
    data = {}
    return render(request, "errors/403.html", data, status=403)


def internal_error(request):
    return render(request, "errors/500.html", status=500)