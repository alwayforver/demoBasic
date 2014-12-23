from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from overviews.models import News, Tweet

def index(request):
    
    return render(request,"index.html")