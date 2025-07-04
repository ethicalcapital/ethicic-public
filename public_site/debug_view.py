from django.shortcuts import render


def debug_width_view(request):
    return render(request, "public_site/debug_width.html")
