from django.shortcuts import render


def inline_test_view(request):
    return render(request, "public_site/inline_test.html")
