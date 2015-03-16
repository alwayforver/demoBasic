import os
import sys
import django
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
import numpy as np

import time
from overviews.models import News
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tweenews.settings')


import django.contrib.sessions

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# print os.e
sys.path.insert(0, os.path.join(BASE_DIR, 'overviews/lib'))
import k_means
import pLSABet
from utility import data_prep, parse_date, prepend_date, find_toptitle_simple, find_topterms_simple


django.setup()
all_start = timezone.make_aware(datetime(2014,12,31,23,23,47), timezone.get_default_timezone())
all_end = timezone.make_aware(datetime(2015,1,4,5,44,17), timezone.get_default_timezone())
cluster_num = 3



def event_running(start_str= '20150101', end_str = '20150102'):
    # time.sleep(10)
    # time.sleep(3)

    start_date, end_date = parse_date(start_str), parse_date(end_str)+timedelta(days = 1)

    if True:
    # if prepend_date(start_str, end_str, 'news_title') not in request.session:

        # time.sleep(3)

        all_news = News.objects.filter(created_at__gte = start_date).filter(created_at__lte = end_date)

        news_title = []
        for i in xrange(len(all_news)):
            news_title.append(all_news[i].title)
        ind2obj = {}
        raw_docs = data_prep(all_news, ind2obj)




        # k_means

        X, Pw_z_km, Pz_d_km, Pd_km, terms = k_means.simple_kmeans(raw_docs, cluster_num)
        # Pw_z, Pz_d, Pd, terms = k_means.simple_kmeans(raw_docs, cluster_num)

        # print np.shape(Pz_d),Pz_d[1,:]

        # print len(np.sum(Pz_d, axis = 0))

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
        print "pLSA done in "+str(time.time() - t0)
        Pw_z = Pw_zs[0]

        top_title = find_toptitle_simple(Pz_d, ind2obj , 3, cluster_num)

        top_term = find_topterms_simple(Pw_z, terms, 3, cluster_num)

        # print top_title
        
        # print top_title[0]

        event_info_list = []

        for i in xrange(cluster_num):
            event_info_list.append( zip(top_title[i], top_term[i]))
        # print event_info_list[0]

        top_title = find_toptitle_simple(Pz_d[:-1,:], news_title , 5, cluster_num)
        top_term = find_topterms_simple(Pw_z[:, :-1], terms, 5, cluster_num)

        # print 'm',Pz_d_km

        # print np.sum(Pz_d_km,)
        # print Pz_d_km[0,:]


        # print 'j', Pz_d[]


        print 'jj',Pz_d[0,:]
        print top_title[0]
        print top_term[0]
    # context = { 'all_news': all_news , 'length':len(news_title)}
    
    return ('OK')


if __name__ == '__main__':

    # event_running()

    # print "Starting club population script..."

    # start_date = datetime(2015,1,1)
    # end_date = datetime(2015,1,2)
    # all_news = News.objects.filter(created_at__gte = start_date).filter(created_at__lte = end_date)


    # raw_docs = []
    # for each in all_news:
    #     raw_docs.append(each.raw_text)
    # # return raw_docs

    # km, order_centroids, terms = k_means.simple_kmeans(raw_docs, 10)


    # print django.contrib.sessions.SESSION_COOKIE_AGE


    # print all_news


    # all_news =  News.objects.all()

    # minD = timezone.make_aware(datetime(2015,3,15), timezone.get_default_timezone())
    # maxD = timezone.make_aware(datetime(2011,1,1), timezone.get_default_timezone())
    # for each in all_news:
    #     if each.created_at< minD:
    #         minD = each.created_at
    #     if each.created_at>maxD:
    #         maxD = each.created_at
    # print "min", minD
    # print "max", maxD

    # PLSA test
    event_running()

