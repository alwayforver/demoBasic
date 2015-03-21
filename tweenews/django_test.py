import os
import sys
import django
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from scipy.sparse import csr_matrix, coo_matrix
from django.core.files import File
import pickle
import time
from overviews.models import News
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tweenews.settings')


# 'DJANGO_SETTINGS_MODULE'  = 'tweenews.settings'
import django.contrib.sessions

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'overviews/lib'))
import k_means
from k_means import calc_Pd, calc_Pe_z, km_initialize
import pLSABet
from utility import find_toptitle_dID, PLSACache, array2csr_matrix, csr_matrix2array, selectTopic, weightX, get_ticks, data_prep, parse_date, prepend_date, find_toptitle_simple, find_topterms_simple, calc_entity_matrix, inittime


django.setup()
all_start = timezone.make_aware(
    datetime(2014, 12, 31, 23, 23, 47), timezone.get_default_timezone())
all_end = timezone.make_aware(
    datetime(2015, 1, 4, 5, 44, 17), timezone.get_default_timezone())
cluster_num = 30


class A:

    def __init__(self):
        self.session = {}

request = A()


numX = 4
aspect_num = 20


def event_running(start_str='20150101', end_str='20150102'):

    start_date, end_date = parse_date(
        start_str), parse_date(end_str) + timedelta(days=1)

    if True:
        # if prepend_date(start_str, end_str, 'news_title') not in request.session:
        # time.sleep(3)
        all_news = News.objects.filter(
            created_at__gte=start_date).filter(created_at__lte=end_date)

        # Vectorizor and raw data preparation
        news_title = []
        news_entities = []
        news_DT = []

        for i in xrange(len(all_news)):
            news_title.append(all_news[i].title)
            news_entities.append(all_news[i].entities)
            news_DT.append(get_ticks(all_news[i].created_at))

        ind2obj = {}
        raw_docs = data_prep(all_news, ind2obj)
        vectorizer = TfidfVectorizer(stop_words='english', max_features=10000)
        X = vectorizer.fit_transform(raw_docs)
        terms = vectorizer.get_feature_names()

        # should be in this order
        entityTypes = ['person', 'place', 'org']

        # reverse_voc a dict for lists of entity terms
        Xe, reverse_voc = calc_entity_matrix(news_entities, entityTypes)

        # reweight
        Xe['person'] = Xe['person'] * 0.3
        Xe['place'] = Xe['place'] * 0.3
        Xe['org'] = Xe['org'] * 0.3

        # Data list preparation
        data = [X]
        for each_type in entityTypes:
            data.append(Xe[each_type])
        data.append(news_DT)

        # inits preparation
        inits_notime, labels_km = km_initialize(
            X, Xe, entityTypes, cluster_num)

        mu_km, sigma_km = inittime(news_DT, cluster_num, labels_km)
        inits = inits_notime + [mu_km, sigma_km]

        # run PLSA

        t0 = time.time()
        Learn = (1, 10)
        selectTime = 1
        numX = 4
        # K=30
        wt = 0.5
        lambdaB = 0.001

        Pw_zs = None
        Pw_zs, Pz_d, Pd, mu, sigma, Li = pLSABet.pLSABet(
                selectTime, numX, Learn, data, inits, wt, lambdaB)

        cluster_num_ = cluster_num
        itercounter = 0
        while(Pw_zs)==None:
            itercounter+=1
            print "###############################################################"
            print "now PLSA rerun", itercounter, "current #", cluster_num_
            cluster_num_ -= 1
            inits_notime, labels_km = km_initialize(
            X, Xe, entityTypes, cluster_num_)
            mu_km, sigma_km = inittime(news_DT, cluster_num_, labels_km)
            inits = inits_notime + [mu_km, sigma_km]


            Pw_zs, Pz_d, Pd, mu, sigma, Li = pLSABet.pLSABet(
                selectTime, numX, Learn, data, inits, wt, lambdaB)
            

        print "pLSA done in " + str(time.time() - t0)

       


        # for each in entityTypes:

        Pw_z = Pw_zs[0]
        Pp_z = Pw_zs[1]
        Pl_z = Pw_zs[2]
        Po_z = Pw_zs[3]

        top_title = find_toptitle_simple(Pz_d, ind2obj, 5)
        top_term = find_topterms_simple(Pw_z, terms, 5)
        # top_entity = find_topterms_simple(Pp_z, reverse_voc['place'],5, cluster_num)
        top_person = find_topterms_simple(
            Pp_z, reverse_voc['person'], 5)
        top_place = find_topterms_simple(
            Pl_z, reverse_voc['place'], 5)
        top_org = find_topterms_simple(
            Po_z, reverse_voc['org'], 5)

        # print top_title

        korea_event = 0
        for i in xrange(len(top_title)):
            # print top_title[i]
            if 'Ohio' in top_term[i]:
                print top_title[i]
                print top_term[i]
                print top_person[i]
                print top_place[i]
                print top_org[i]
                korea_event = i

        n_wdxPz_wds = []
        for i in range(numX):
            n_wdxPz_wds.append(weightX(data[i], Pw_zs[i], Pz_d))

        event_info_list = []

        for i in xrange(cluster_num_):
            event_info_list.append(zip(top_title[i], top_term[i]))

        cur_cache = PLSACache(data, n_wdxPz_wds, ind2obj, terms, reverse_voc)

        cache_file = File(open('./media/cache' + start_str + end_str, 'w'))
        pickle.dump(cur_cache, cache_file)
        cache_file.close()

        tt0 = time.time()

        # all_tweets = set()
        # for i in xrange(len(all_news)):
        #     print "dealing with news",i
        #     all_tweets.update(set(all_news[i].tweet_set.all()))
        # print len(all_tweets)

        tt1 = time.time()

        print "time running", tt1-tt0



    return korea_event


def aspect_running(start_str='20150101', end_str='20150102', event='0'):
    try:
        cache_file = open('./media/cache' + start_str + '_' + end_str)
        cur_cache = pickle.load(cache_file)
        cache_file.close()

        data, n_wdxPz_wds, ind2obj, terms, reverse_voc = cur_cache.Xdata, cur_cache.n_wdxPz_wds, cur_cache.ind2obj, cur_cache.terms, cur_cache.reverse_voc

        Xevents, dID = selectTopic(data[:numX], n_wdxPz_wds, event)

        print "dID", len(dID)
        DT = data[-1]
        DTevent = np.array(DT)[dID]

        data = Xevents + [DTevent]
        X = data[0]
        entityTypes = ['person', 'place', 'org']

        Xe = {}
        for i in xrange(len(entityTypes)):
            Xe[entityTypes[i]] = data[i + 1]

        inits_notime, labels_km = km_initialize(X, Xe, entityTypes, aspect_num)

        mu_km, sigma_km = inittime(DTevent, aspect_num, labels_km)

        inits = inits_notime + [mu_km, sigma_km]

        # run PLSA

        t0 = time.time()
        Learn = (1, 10)
        selectTime = 1

        # K=30
        wt = 0.5
        lambdaB = 0

        Pw_zs = None
        Pw_zs, Pz_d, Pd, mu, sigma, Li = pLSABet.pLSABet(
                selectTime, numX, Learn, data, inits, wt, lambdaB)

        aspect_num_ = aspect_num
        itercounter = 0
        while(Pw_zs)==None:
            itercounter+=1
            print "###############################################################"
            print "now PLSA rerun", itercounter, "current #", aspect_num_
            aspect_num_ -= 1
            inits_notime, labels_km = km_initialize(
            X, Xe, entityTypes, aspect_num_)
            mu_km, sigma_km = inittime(DTevent, aspect_num_, labels_km)
            inits = inits_notime + [mu_km, sigma_km]


            Pw_zs, Pz_d, Pd, mu, sigma, Li = pLSABet.pLSABet(
                selectTime, numX, Learn, data, inits, wt, lambdaB)
        print "pLSA done in " + str(time.time() - t0)

        # for each in entityTypes:
        Pw_z = Pw_zs[0]
        Pp_z = Pw_zs[1]
        Pl_z = Pw_zs[2]
        Po_z = Pw_zs[3]

        # print type(Pw_z)
        # print Pw_z.shape
        top_title = find_toptitle_dID(Pz_d, ind2obj, 5, dID)
        top_term = find_topterms_simple(Pw_z, terms, 5)
        # top_entity = find_topterms_simple(Pp_z, reverse_voc['place'],5, aspect_num)
        top_person = find_topterms_simple(
            Pp_z, reverse_voc['person'], 5)
        top_place = find_topterms_simple(
            Pl_z, reverse_voc['place'], 5)
        top_org = find_topterms_simple(Po_z, reverse_voc['org'], 5)

        # for i in xrange(aspect_num):
        #     print top_title[i]

    except IOError as e:
        print "Unable to open file"

    return data
if __name__ == '__main__':

    # event_running()

    # print "Starting club population script..."

    # start_date = datetime(2015,1,1)
    # end_date = datetime(2015,1,2)
    # all_news = News.objects.filter(created_at__gte = start_date).filter(created_at__lte = end_date)

    # raw_docs = []
    # for each in all_news:
    #     raw_docs.append(each.raw_text)
    # return raw_docs

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
    # i = event_running()
    # print "###########"

    # for i in xrange(10):
    aspect_running(event=0)
