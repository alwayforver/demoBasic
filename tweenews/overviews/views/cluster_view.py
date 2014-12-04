from django.shortcuts import render, render_to_response
from django.http import HttpResponse

def cluster_view(request):
    context = {}
    return render(request, 'cluster.html', context)