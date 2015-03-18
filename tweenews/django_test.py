import os
import sys
import django
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

import time
from overviews.models import News
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tweenews.settings')


# 'DJANGO_SETTINGS_MODULE'  = 'tweenews.settings'
import django.contrib.sessions

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# print os.e
sys.path.insert(0, os.path.join(BASE_DIR, 'overviews/lib'))
import k_means
from k_means import calc_Pd, calc_Pe_z
import pLSABet
from utility import get_ticks, data_prep, parse_date, prepend_date, find_toptitle_simple, find_topterms_simple,calc_entity_matrix, inittime


django.setup()
all_start = timezone.make_aware(datetime(2014,12,31,23,23,47), timezone.get_default_timezone())
all_end = timezone.make_aware(datetime(2015,1,4,5,44,17), timezone.get_default_timezone())
cluster_num = 10



def event_running(start_str= '20150101', end_str = '20150102'):
    # time.sleep(10)
    # time.sleep(3)

    start_date, end_date = parse_date(start_str), parse_date(end_str)+timedelta(days = 1)

    if True:
    # if prepend_date(start_str, end_str, 'news_title') not in request.session:

        # time.sleep(3)

        all_news = News.objects.filter(created_at__gte = start_date).filter(created_at__lte = end_date)

        news_title = []
        news_entities = []
        news_DT = []


        for i in xrange(len(all_news)):
            news_title.append(all_news[i].title)
            news_entities.append(all_news[i].entities)
            news_DT.append(get_ticks(all_news[i].created_at))



        ind2obj = {}
        raw_docs = data_prep(all_news, ind2obj)
        vectorizer = TfidfVectorizer( stop_words='english')
        #    vectorizer = TfidfVectorizer( stop_words=None)
        X = vectorizer.fit_transform(raw_docs)
        terms = vectorizer.get_feature_names()
        # k_means

        Pw_z_km, Pz_d_km, labels_km = k_means.simple_kmeans(X, cluster_num)

        Pd_km = calc_Pd(raw_docs)
        mu_km,sigma_km = inittime(news_DT, cluster_num, labels_km)

        entityTypes = ['person','org', 'place']

        # reverse_voc a dict for lists of entity terms


        Xe, reverse_voc = calc_entity_matrix(news_entities, entityTypes)

        Pp_z_km = calc_Pe_z(labels_km, Xe['person'], cluster_num)
        Pl_z_km = calc_Pe_z(labels_km, Xe['place'], cluster_num)
        Po_z_km = calc_Pe_z(labels_km, Xe['org'], cluster_num)


        # print np.shape(Pp_z)
        # print Pp_z, type(Pp_z)
        # print Pw_z_km, np.shape(Pw_z_km)
        # print Pp_z_km, np.shape(Pp_z_km)
        # print type(X)
        # print np.shape(X)
        # Pw_z, Pz_d, Pd, terms = k_means.simple_kmeans(raw_docs, cluster_num)
        # print np.shape(Pz_d),Pz_d[1,:]
        # print len(np.sum(Pz_d, axis = 0))

        t0 = time.time()
        Learn=(1,10)
        selectTime = 1
        numX = 4
        #K=30
        # data = [X, Xe['person']*0.3]
        Xp = Xe['person']*0.3
        Xl = Xe['place']*0.3
        Xo = Xe['org']*0.3
        data = [X, Xp, Xl, Xo, news_DT]

        # print "asd",Xp.shape
        #mu_km, sigma_km= inittime(DT,K,labels)

        # print "this is ", np.shape(Pw_z_km), np.shape(Pp_z_km)
        inits = [Pz_d_km,Pw_z_km, Pp_z_km, Pl_z_km, Po_z_km, mu_km, sigma_km]
        # inits = [Pz_d_km,Pw_z_km]

        # print "Pw_z type",type(Pw_z_km)

        wt = 0.5
        lambdaB = 0
        # data = [Xs,DT]
        # inits = [Pz_d,Pw_z, Pp_z,Pl_z,Po_z,mu,sigma]   

        Pw_zs,Pz_d,Pd,mu,sigma,Li = pLSABet.pLSABet(selectTime,numX,Learn,data,inits,wt,lambdaB)
        print "pLSA done in "+str(time.time() - t0)

        Pw_z = Pw_zs[0]
        Pp_z = Pw_zs[1]
        Pl_z = Pw_zs[2]
        Po_z = Pw_zs[3]


        top_title = find_toptitle_simple(Pz_d, ind2obj , 5, cluster_num)
        top_term = find_topterms_simple(Pw_z, terms, 5, cluster_num)
        # top_entity = find_topterms_simple(Pp_z, reverse_voc['place'],5, cluster_num)
        top_person= find_topterms_simple(Pp_z, reverse_voc['person'], 5, cluster_num)
        top_place= find_topterms_simple(Pl_z, reverse_voc['place'], 5, cluster_num)
        top_org= find_topterms_simple(Po_z, reverse_voc['org'], 5, cluster_num)


        # print top_title
        
        for i in xrange(len(top_title)):
            # print top_title[i]
            if 'korea' in top_term[i]:
                print top_title[i]
                print top_term[i]
                print top_person[i]
                print top_place[i]

                print top_org[i]


                # print top_entity[i]

        print "haha",mu, sigma

        event_info_list = []

        for i in xrange(cluster_num):
            event_info_list.append( zip(top_title[i], top_term[i]))
        # print event_info_list[0]

        # print 'm',Pz_d_km

        # print np.sum(Pz_d_km,)
        # print Pz_d_km[0,:]
        # print 'j', Pz_d[]
        # print 'jj',Pz_d[0,:]
        # print top_title[0]
        # print top_term[0]
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

