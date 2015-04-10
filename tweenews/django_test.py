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


import django.contrib.sessions

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'overviews/lib'))
#sys.path.append(os.path.join(BASE_DIR, 'overviews/lib'))
import k_means
from k_means import calc_Pd, calc_Pe_z, km_initialize
import pLSABet
from utility import filterEvent, find_topterms_dic, find_toptitle_dID, PLSACache, array2csr_matrix, csr_matrix2array, selectTopic, weightX, get_ticks, data_prep, parse_date, prepend_date, find_toptitle_simple, find_topterms_simple, calc_entity_matrix, inittime
from GraphData import drawWordCloud, dataTextGen, aspectTextGen, EntityGraphData, textGen, drawLineDist
from summarization import summarization
from tweetAnalysis import MySentiWordExtractor, SentiTweet, getSentiPercentageDic, getSentiPercentage, LRSentiClassifier

django.setup()
all_start = timezone.make_aware(
    datetime(2014, 12, 31, 23, 23, 47), timezone.get_default_timezone())
all_end = timezone.make_aware(
    datetime(2015, 1, 4, 5, 44, 17), timezone.get_default_timezone())
cluster_num = 30
topk = 10
debug = 1
sentiCL = LRSentiClassifier()


class A:

    def __init__(self):
        self.session = {}

request = A()


numX = 4
aspect_num = 5


def event_running(start_str='20150308', end_str='20150312'):

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

        # print "data shape",type(data[1])
        # inits preparation
        inits_notime, labels_km = km_initialize(
            X, Xe, entityTypes, cluster_num)

        mu_km, sigma_km = inittime(news_DT, cluster_num, labels_km)
        inits = inits_notime + [mu_km, sigma_km]

        # run PLSA

        # parameter setting
        t0 = time.time()
        Learn = (1, 10)
        selectTime = 1
        numX = 4
        # K=30
        wt = 0.5
        lambdaB = 0.2

        Pw_zs = None
        Pw_zs, Pz_d, Pd, mu, sigma, Li = pLSABet.pLSABet(
            selectTime, numX, Learn, data, inits, wt, lambdaB)

        cluster_num_ = cluster_num
        itercounter = 0
        while(Pw_zs) == None:
            itercounter += 1
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
        
        Pw_zs, Pz_d,mu,sigma, cluster_num_ = filterEvent(Pw_zs, Pz_d, Pd, mu, sigma)

        # for each in entityTypes:
        Pw_z = Pw_zs[0]
        Pp_z = Pw_zs[1]
        Pl_z = Pw_zs[2]
        Po_z = Pw_zs[3]
        # print 'shape', cluster_num_, Pw_z.shape, Pp_z.shape

        # print 'Pp_z size', Pp_z.shape
        # find tops
        top_title = find_toptitle_simple(Pz_d, ind2obj, 5)
        top_term = find_topterms_simple(Pw_z, terms, 5)
        top_term_dic = find_topterms_dic(Pw_z, terms, 30)

        target_event = 0
        for i in xrange(len(top_title)):
            # print top_title[i]
            # print "###########"
            # print "now its event", i
            for title in top_title[i]:
                #     print title
                if 'Korea' in title:
                    target_event = i

        n_wdxPz_wds = []
        for i in range(numX):
            n_wdxPz_wds.append(weightX(data[i], Pw_zs[i], Pz_d))

        event_info_list = []

        opinion_percent = []

        for event in xrange(cluster_num_):
            print "##################### Event", event, "#################"
            print
            # event = target_event
            _, dID = selectTopic(data[:numX], n_wdxPz_wds, event)
            event_news_list = []
            print "did length is", len(dID)
            print "top title"
            for i in xrange(5):
                print top_title[event][i].encode("utf-8")
            print
            for each in dID:
                event_news_list.append(ind2obj[each])
                # X = vectorizer.fit_transform()
                # print ind2obj[each].title
            word_dist = Pw_z[:, event].T
            time_mu = mu[event]
            time_sigma = sigma[event]
            event_tweet_list = []
            for i in xrange(len(event_news_list)):
                # print "dealing with news",i
                event_tweet_list += list(event_news_list[i].tweet_set.all())

            news_summary, tweets_summary, tweets, tweets_rele, sentiment = summarization(
                sentiCL, event_news_list, event_tweet_list, word_dist, vectorizer, 
                time_mu, time_sigma, 5) ## arg event for output purpose jingjing

            news_summary.sort(key = lambda s: s.created_at)
            news_summary_text = ""
            for i in xrange(len(news_summary)):
                news_summary_text+=(str(news_summary[i].created_at)[:10]+'  '+news_summary[i].title+'\n\n')
            news_summary_text = news_summary_text[:-2]
            print news_summary_text


            # opinion_percent.append((getSentiPercentageDic(sentiCL, tweets, tweets_rele)))

            #print "opinion for event ", event, getSentiPercentage(sentiCL, tweets, tweets_rele)

        for i in xrange(cluster_num_):
            event_info_list.append(zip(top_title[i], top_term[i]))
        # print 'beforesave',n_wdxPz_wds[0].shape
        cur_cache = PLSACache(
            data, Pw_zs, n_wdxPz_wds, ind2obj, terms, reverse_voc, vectorizer)

        cache_file = File(
            open('./media/cache' + start_str + '_' + end_str, 'w'))
        pickle.dump(cur_cache, cache_file)
        cache_file.close()

    return target_event


def aspect_running(start_str='20150101', end_str='20150102', event='0'):
    try:
        print "start aspect....."
        cache_file = open('./media/cache' + start_str + '_' + end_str)
        cur_cache = pickle.load(cache_file)
        cache_file.close()
        event = int(event)

        data, n_wdxPz_wds, ind2obj, terms, reverse_voc, prev_Pw_zs, vectorizer = cur_cache.Xdata, cur_cache.n_wdxPz_wds, cur_cache.ind2obj, cur_cache.terms, cur_cache.reverse_voc, cur_cache.Pw_zs, cur_cache.vectorizer
        Xevents, dID = selectTopic(data[:numX], n_wdxPz_wds, event)

        # print "dID", len(dID)
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
        while(Pw_zs) == None:
            itercounter += 1
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
        # print 'mu, sigma', mu, sigma
        # print "shape", Pz_d.shape

        t1 = time.time()
        aspect_n_wdxPz_wds = []
        for i in xrange(numX):
            aspect_n_wdxPz_wds.append(weightX(Xevents[i], Pw_zs[i], Pz_d))

        t2 = time.time()
        Xaspects_list = []
        news_summary_list = []
        tweets_summary_list = []

        for aspect in xrange(aspect_num_):
            Xaspects, aspect_dID = selectTopic(
                data[:numX], aspect_n_wdxPz_wds, aspect)
            Xaspects_list.append(Xaspects)
            event_news_list = []
            # print dID
            # print "top title"
            # print "size of news list", len(event_news_list)
            # for i in xrange(5):
            #     print top_title[event][i].encode("utf-8")
            # print
            # for each in aspect_dID:
            #     event_news_list.append(ind2obj[each])
            # X = vectorizer.fit_transform()
            # print ind2obj[each].title
            # word_dist = Pw_z[:, aspect].T
            # time_mu = mu[aspect]
            # time_sigma = sigma[aspect]
            # event_tweet_list = []

            # for i in xrange(len(event_news_list)):
            #     event_tweet_list+=list(event_news_list[i].tweet_set.all())

            # news_summary, tweets_summary, tweets, tweets_rele, sentiment = summarization(sentiCL, event_news_list, event_tweet_list, word_dist, vectorizer, time_mu, time_sigma, topk, debug)
            # print "hub"
            # news_summary_text = '\n\n'.join([n.title for n in news_summary])

            # print "news summary is"
            # print news_summary_text
            # print "hah"
            # news_summary_list.append(news_summary_text)

            # tweets_summary_text = '\n\n'.join(tweets_summary)

            # print "tweets summary is"
            # print tweets_summary_text
            # print
            # tweets_summary_list.append(tweets_summary_text)

        t3 = time.time()
        gd = EntityGraphData(1, event, aspect_num_, reverse_voc, prev_Pw_zs[
                             1], prev_Pw_zs[2], prev_Pw_zs[3], Xaspects_list, Pp_z, Pl_z, Po_z)

        t4 = time.time()

        top_title = find_toptitle_dID(Pz_d, ind2obj, 5, dID)
        top_term = find_topterms_simple(Pw_z, terms, 5)
        # top_entity = find_topterms_simple(Pp_z, reverse_voc['place'],5, aspect_num)
        top_term_dict = find_topterms_dic(Pw_z, terms, 30)

        print top_title
        t5 = time.time()
        # for i in xrange(aspect_num):
        # print top_title[i]
        # print t2-t1, t3-t2, t4-t3, t5-t4
    except IOError as e:
        print "Unable to open file"

    return data

if __name__ == '__main__':

    # myextractor = MySentiWordExtractor()
    # print "bad#a" in myextractor.term_sent,  myextractor.get_score(('don\'t','r'))

    i = event_running()
    # aspect_running(event=i)
    # f = open('testtime')
    # [sentiCL, news, tweets, word_distribution, vectorizer, mu, sigma, topk, debug] = pickle.load(f)

    # summarization(sentiCL, news, tweets, word_distribution, vectorizer, mu, sigma, topk, debug)
