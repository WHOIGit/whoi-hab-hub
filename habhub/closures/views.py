from django.shortcuts import render
from django.views.generic import View, DetailView, ListView

from .models import ClosureArea
# Create your views here.


class ClosureHomeView(ListView):
    model = ClosureArea
    template_name = 'closures/closures_home.html'
    context_object_name = 'closures'
