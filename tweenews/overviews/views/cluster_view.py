from django.shortcuts import render, render_to_response
from django.http import HttpResponse
import util

def cluster_view(request):
    context = {'Json_Filename':'test1.json'}
    util.test()
    return render(request, 'cluster_test.html', context)
