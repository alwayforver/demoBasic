from django.shortcuts import render, render_to_response
import sys, os
from django.http import HttpResponse
from overviews.models import News, Tweet, MetaInfo
from overviews.forms import StartEndDateForm
import time
from datetime import datetime, timedelta
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from scipy.sparse import csr_matrix

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

sys.path.insert(0, os.path.join(BASE_DIR, 'lib'))
import k_means
from utility import data_prep, parse_date, prepend_date, find_toptitle_simple, find_topterms_simple, calc_entity_matrix
import pLSABet

# from django.core.contex_processors import csrf

# import util

debug = True

all_start = timezone.make_aware(datetime(2014,12,31,23,23,47), timezone.get_default_timezone())
all_end = timezone.make_aware(datetime(2015,1,4,5,44,17), timezone.get_default_timezone())

cluster_num = 10

def event_view(request):

    # c = {}
    # c.update(csrf(request))
    valid_input = False
    calculation = False
    # valid_input = False
    start_date = None
    end_date = None
    start_str = None
    end_str = None
    input_start_date= None
    input_end_date = None
    # print request.POST
    meta = MetaInfo.objects.all()[0]
    all_start = meta.news_start_date
    all_end = meta.news_end_date
    if request.method == 'POST' and 'sdate' in request.POST and 'edate' in request.POST:
        input_start_date, input_end_date = request.POST['sdate'], request.POST['edate']

        start_date = parse_date(input_start_date)
        end_date = parse_date(input_end_date)

        # print input_start_date, input_end_date
        # print start_date, end_date
        valid_input = True


        if debug == True:
            condition = start_date!=None and end_date!=None
        else:
            condition = start_date!=None and end_date!=None and start_date>= all_start and end_date<=all_end and start_date<=end_date
        
        if condition:
            start_str = input_start_date.replace('-','')
            end_str = input_end_date.replace('-','')  
            calculation = True



    # print start_date, end_date
    # print start_date, end_date,calculation, 
    context = {'all_start':all_start,'all_end':all_end, 'input_end_date': input_end_date,'input_start_date': input_start_date, 'valid_input':valid_input, 'calculation': calculation, 'start_str':start_str, 'end_str':end_str}
    return render(request, 'eventDiscovery.html', context)


def event_running(request, start_str= '19901025', end_str = '19901025'):
    # time.sleep(10)
    # time.sleep(3)

    start_date, end_date = parse_date(start_str), parse_date(end_str)+timedelta(days = 1)


    if True:
    # if prepend_date(start_str, end_str, 'news_title') not in request.session:
        # time.sleep(3)
        all_news = News.objects.filter(created_at__gte = start_date).filter(created_at__lte = end_date)

        news_title = []
        news_entities =[]
        for i in xrange(len(all_news)):
            news_title.append(all_news[i].title)
            news_entities.append(all_news[i].entities)


        ind2obj = {}
        raw_docs = data_prep(all_news, ind2obj)
        # k_means
        X, Pw_z_km, Pz_d_km, Pd_km, terms = k_means.simple_kmeans(raw_docs, cluster_num)

        print type(X)
        Xp, Xl, Xo = calc_entity_matrix(news_entities)
        # print X.shape()

        t0 = time.time()
        Learn=(1,10)
        selectTime = 0
        numX = 1
        #K=30
        data = [X]
        #mu_km, sigma_km= inittime(DT,K,labels)
        inits = [Pz_d_km,Pw_z_km]
        wt = 0.5
        lambdaB = 0
        # data = [Xs,DT]
        # inits = [Pz_d,Pw_z, Pp_z,Pl_z,Po_z,mu,sigma]        
        Pw_zs,Pz_d,Pd,mu,sigma,Li = pLSABet.pLSABet(selectTime,numX,Learn,data,inits,wt,lambdaB)
        # print "pLSA done in "+str(time.time() - t0)
        Pw_z = Pw_zs[0]

        top_title = find_toptitle_simple(Pz_d, ind2obj , 5, cluster_num)
        top_term = find_topterms_simple(Pw_z, terms, 5, cluster_num)

        # print 'm',Pz_d_km

        # print np.sum(Pz_d_km,)
        # print Pz_d_km[:,0]


        # print 'j', Pz_d
        # print 'jj',Pz_d[:,0]
        # print top_title[0]
        # print top_term[0]

        
        request.session[prepend_date(start_str, end_str, 'top_title')] = top_title
        request.session[prepend_date(start_str, end_str, 'top_term')] = top_term
        # request.session[prepend_date(start_str, end_str, 'X')] = X

        # Need to store event assignment in this step

    # context = { 'all_news': all_news , 'length':len(news_title)}
    
    return HttpResponse('OK')

def event_display(request, start_str, end_str):

    top_title = request.session.get(prepend_date(start_str, end_str, 'top_title'),[])
    top_term = request.session.get(prepend_date(start_str, end_str, 'top_term'),[])

    # X = request.session.get(prepend_date(start_str, end_str, 'X'), [])

    # print X

    event_info_list = []

    for i in xrange(cluster_num):
        event_info_list.append( zip(top_title[i], top_term[i]))

    context = {'start_str':start_str, 'end_str':end_str, 'event_info_list':event_info_list}
    return render(request, 'eventDisplay.html', context)

def aspect_discovery(request, start_str='19901025', end_str='19901025', event=1):

    event = int(event)

    top_title = request.session.get(prepend_date(start_str, end_str, 'top_title'),[])[event]

    context = {'start_str':start_str, 'end_str':start_str, 'event':event, 'event_str': event+1, 'top_title':top_title}


    return render(request, 'aspectDiscovery.html', context)


def aspect_running(request, start_str='19901025', end_str = '19901025', event = 0):


    return HttpResponse('OK')

if __name__ == '__main__':
    print parse_date('15-02-05')

