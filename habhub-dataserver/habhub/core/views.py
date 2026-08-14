from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def health_check(request):
    """Liveness endpoint for the AWS load balancer. Deliberately does no
    DB/cache/template work so it stays cheap and independent of those
    dependencies' health."""
    return HttpResponse("OK")
