from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from .models import Location

class TopView(TemplateView):
    template_name = "top.html"

class LocationView(ListView):
    model = Location
    template_name = "list.html"
    paginate_by = 3
