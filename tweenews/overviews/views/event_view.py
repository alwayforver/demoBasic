from django.shortcuts import render, render_to_response
import sys
import os
from django.http import HttpResponse
from overviews.models import News, Tweet, MetaInfo
from overviews.forms import StartEndDateForm
import time
from datetime import datetime, timedelta
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import numpy as np
import pickle
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from django.core.files import File
sys.path.insert(0, os.path.join(BASE_DIR, 'lib'))
import k_means
from k_means import calc_Pd, calc_Pe_z, km_initialize
import pLSABet
from utility import find_toptitle_dID, PLSACache, array2csr_matrix, csr_matrix2array, selectTopic, weightX, get_ticks, data_prep, parse_date, prepend_date, find_toptitle_simple, find_topterms_simple, calc_entity_matrix, inittime

# from django.core.contex_processors import csrf

debug = True

all_start = timezone.make_aware(
    datetime(2014, 12, 31, 23, 23, 47), timezone.get_default_timezone())
all_end = timezone.make_aware(
    datetime(2015, 1, 4, 5, 44, 17), timezone.get_default_timezone())

cluster_num = 30
aspect_num = 5
numX = 4


def event_view(request):
    valid_input = False
    calculation = False
    # valid_input = False
    start_date = None
    end_date = None
    start_str = None
    end_str = None
    input_start_date = None
    input_end_date = None
    meta = MetaInfo.objects.all()[0]
    all_start = meta.news_start_date
    all_end = meta.news_end_date
    if request.method == 'POST' and 'sdate' in request.POST and 'edate' in request.POST:
        input_start_date, input_end_date = request.POST[
            'sdate'], request.POST['edate']

        start_date = parse_date(input_start_date)
        end_date = parse_date(input_end_date)

        valid_input = True

        if debug == True:
            condition = start_date != None and end_date != None
        else:
            condition = start_date != None and end_date != None and start_date >= all_start and end_date <= all_end and start_date <= end_date

        if condition:
            start_str = input_start_date.replace('-', '')
            end_str = input_end_date.replace('-', '')
            calculation = True
    context = {'all_start': all_start, 'all_end': all_end, 'input_end_date': input_end_date, 'input_start_date':
               input_start_date, 'valid_input': valid_input, 'calculation': calculation, 'start_str': start_str, 'end_str': end_str}
    return render(request, 'eventDiscovery.html', context)


def event_running(request, start_str='19901025', end_str='19901025'):
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
        Learn = (1, 20)
        selectTime = 1

        wt = 0.5
        lambdaB = 0

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
        top_person = find_topterms_simple(
            Pp_z, reverse_voc['person'], 5)
        top_place = find_topterms_simple(
            Pl_z, reverse_voc['place'], 5)
        top_org = find_topterms_simple(
            Po_z, reverse_voc['org'], 5)

        n_wdxPz_wds = []
        for i in range(numX):
            n_wdxPz_wds.append(weightX(data[i], Pw_zs[i], Pz_d))

        request.session[
            prepend_date(start_str, end_str, 'top_title')] = top_title
        request.session[
            prepend_date(start_str, end_str, 'top_term')] = top_term
        request.session[
            prepend_date(start_str, end_str, 'top_person')] = top_person
        request.session[
            prepend_date(start_str, end_str, 'top_place')] = top_place
        request.session[prepend_date(start_str, end_str, 'top_org')] = top_org


        print "Finish News side works..."
        print "Start Tweet side"

        # all_tweets = set()
        # for i in xrange(len(all_news)):
        #     print "dealing with news",i
        #     all_tweets.update(set(all_news[i].tweet_set.all()))
        # print len(all_tweets)

        cur_cache = PLSACache(data, n_wdxPz_wds, ind2obj, terms, reverse_voc)

        cache_file = File(
            open('./media/cache' + start_str + '_' + end_str, 'w'))
        pickle.dump(cur_cache, cache_file)
        cache_file.close()

        print ""



    return HttpResponse('OK')


def event_display(request, start_str, end_str):

    top_title = request.session.get(
        prepend_date(start_str, end_str, 'top_title'), [])
    top_term = request.session.get(
        prepend_date(start_str, end_str, 'top_term'), [])
    top_person = request.session.get(
        prepend_date(start_str, end_str, 'top_person'), [])
    top_place = request.session.get(
        prepend_date(start_str, end_str, 'top_place'), [])
    top_org = request.session.get(
        prepend_date(start_str, end_str, 'top_org'), [])

    event_info_list = []

    for i in xrange(len(top_title)):
        event_info_list.append(zip(top_title[i], top_term[i]))

    context = {'start_str': start_str, 'end_str': end_str,
               'event_info_list': event_info_list, 'top_person': top_person}

    return render(request, 'eventDisplay.html', context)


def aspect_discovery(request, start_str='19901025', end_str='19901025', event=1):

    event = int(event)

    top_title = request.session.get(
        prepend_date(start_str, end_str, 'top_title'), [])[event]

    context = {'start_str': start_str, 'end_str': start_str,
               'event': event, 'event_str': event + 1, 'top_title': top_title}

    return render(request, 'aspectDiscovery.html', context)


def aspect_running(request, start_str='19901025', end_str='19901025', event=0):

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

            if aspect_num_ ==1:
                return HttpResponse('OneError')
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

        request.session[prepend_date(
            start_str, end_str, 'event' + str(event) + 'top_title')] = top_title
        request.session[
            prepend_date(start_str, end_str, 'event' + str(event) + 'top_term')] = top_term
        request.session[prepend_date(
            start_str, end_str, 'event' + str(event) + 'top_person')] = top_person
        request.session[prepend_date(
            start_str, end_str, 'event' + str(event) + 'top_place')] = top_place
        request.session[
            prepend_date(start_str, end_str, 'event' + str(event) + 'top_org')] = top_org

    except IOError as e:
        print "Unable to open file"

    return HttpResponse('OK')


def aspect_display(request, start_str, end_str, event=0):
    top_title = request.session.get(
        prepend_date(start_str, end_str, 'event' + str(event) + 'top_title'), [])
    top_term = request.session.get(
        prepend_date(start_str, end_str, 'event' + str(event) + 'top_term'), [])
    top_person = request.session.get(
        prepend_date(start_str, end_str, 'event' + str(event) + 'top_person'), [])
    top_place = request.session.get(
        prepend_date(start_str, end_str, 'event' + str(event) + 'top_place'), [])
    top_org = request.session.get(
        prepend_date(start_str, end_str, 'event' + str(event) + 'top_org'), [])

    event_info_list = []

    for i in xrange(len(top_title)):
        event_info_list.append(zip(top_title[i], top_term[i]))

    context = {'start_str': start_str, 'end_str': end_str,
               'event_info_list': event_info_list}

    return render(request, 'aspectDisplay.html', context)

def aspect_display_noaspect(request, start_str, end_str, event=0):

    top_title = request.session.get(
        prepend_date(start_str, end_str, 'top_title'), [])
    top_term = request.session.get(
        prepend_date(start_str, end_str, 'top_term'), [])
    top_person = request.session.get(
        prepend_date(start_str, end_str, 'top_person'), [])
    top_place = request.session.get(
        prepend_date(start_str, end_str, 'top_place'), [])
    top_org = request.session.get(
        prepend_date(start_str, end_str, 'top_org'), [])

    # X = request.session.get(prepend_date(start_str, end_str, 'X'), [])
    # print top_title

    event_i = int(event)
    top_title = top_title[event_i]
    top_term = top_term[event_i]
    top_person = top_person[event_i]
    top_place = top_place[event_i]
    top_org = top_org[event_i]


    event_info_list = (zip(top_title, top_term))

    context = {'start_str': start_str, 'end_str': end_str,
               'event_info_list': event_info_list}

    return render(request, 'aspectDisplayNoAspect.html', context)
    # return HttpResponse('OK')

if __name__ == '__main__':
    print parse_date('15-02-05')
