from django.shortcuts import render, render_to_response
import sys
import os
import os.path
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
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from wordcloud import WordCloud


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from django.core.files import File
sys.path.insert(0, os.path.join(BASE_DIR, 'lib'))
import k_means
from k_means import calc_Pd, calc_Pe_z, km_initialize
import pLSABet
from utility import filterEventKeyword, rankEventwithTime, filterEvent, find_topterms_dic, find_toptitle_dID, PLSACache, array2csr_matrix, csr_matrix2array, selectTopic, weightX, get_ticks, data_prep, parse_date, prepend_date, find_toptitle_simple, find_topterms_simple, calc_entity_matrix, inittime
from GraphData import drawOpinionPie, drawWordCloud, dataTextGen, aspectTextGen, EntityGraphData, textGen, drawLineDist
from tweetAnalysis import getSentiPercentageDic, getSentiPercentage, LRSentiClassifier
from summarization import summarization


# from django.core.contex_processors import csrf

debug = True

all_start = timezone.make_aware(
    datetime(2014, 12, 31, 23, 23, 47), timezone.get_default_timezone())
all_end = timezone.make_aware(
    datetime(2015, 1, 4, 5, 44, 17), timezone.get_default_timezone())

cluster_num = 40
aspect_num = 4
numX = 4
topk = 5

colors = ["#0B6121", "#FE2E2E", "#01A9DB", "#DBA901", "#A52A2A", "#333333",
                "#00ff00", "#b6fcd5", "#31698a", "#ff00ff", "#7fffd4", "#800000", "#8a2be2"]

graphBuffer = {}
sentiCL = LRSentiClassifier()


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
    keywords = ""
    if request.method == 'POST' and 'sdate' in request.POST and 'edate' in request.POST:
        input_start_date, input_end_date, keywords = request.POST[
            'sdate'], request.POST['edate'], request.POST['keywords']

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
               input_start_date, 'valid_input': valid_input, 'calculation': calculation, 'start_str': start_str, 'end_str': end_str, 'keywords':keywords}
    return render(request, 'eventDiscovery.html', context)


def event_running(request, start_str='19901025', end_str='19901025', keywords = ''):
    start_date, end_date = parse_date(
        start_str), parse_date(end_str) + timedelta(days=1)


    # this function is not yet implemented
    keywords = keywords.strip()
    if len(keywords)==0:
        keywords = []
    else:
        keywords = keywords.split(',')

    # if os.path.exists('./media/cache' + start_str + '_' + end_str) and prepend_date(start_str, end_str, 'top_title') in request.session:
    #     print "exist!"
    if True:
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
        lambdaB = 0.2

        Pw_zs = None
        Pw_zs, Pz_d, Pd, mu, sigma, Li = pLSABet.pLSABet(
            selectTime, numX, Learn, data, inits, wt, lambdaB, debug)

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
                selectTime, numX, Learn, data, inits, wt, lambdaB, debug)
        print "pLSA done in " + str(time.time() - t0)

        # Pw_zs, Pz_d, mu, sigma, cluster_num_ = filterEvent(Pw_zs, Pz_d, Pd, mu, sigma)
        Pw_zs, Pz_d, mu, sigma, cluster_num_ = filterEventKeyword(Pw_zs, Pz_d, Pd, mu, sigma, terms)

        Pw_z = Pw_zs[0]
        Pp_z = Pw_zs[1]
        Pl_z = Pw_zs[2]
        Po_z = Pw_zs[3]

        top_title = find_toptitle_simple(Pz_d, ind2obj, topk)
        # top_term = find_topterms_simple(Pw_z, terms, topk)
        top_term_dic = find_topterms_dic(Pw_z, terms, 30)

        n_wdxPz_wds = []
        for i in range(numX):
            n_wdxPz_wds.append(weightX(data[i], Pw_zs[i], Pz_d))

        news_summary_list = []
        tweets_summary_list = []

        opinion_percent = []

        for event in xrange(cluster_num_):
            print "##################### Event", event, "#################"
            print
            # event = target_event
            _, dID = selectTopic(data[:numX], n_wdxPz_wds, event)
            event_news_list = []
            # print dID
            # print "top title"
            # print "size of news list", len(event_news_list)
            # for i in xrange(5):
            #     print top_title[event][i].encode("utf-8")
            # print
            for each in dID:
                event_news_list.append(ind2obj[each])
                # X = vectorizer.fit_transform()
                # print ind2obj[each].title
            word_dist = Pw_z[:, event].T
            time_mu = mu[event]
            time_sigma = sigma[event]
            event_tweet_list = []

            for i in xrange(len(event_news_list)):
                event_tweet_list += list(event_news_list[i].tweet_set.all())
            news_summary, tweets_summary, tweets, tweets_rele, sentiment = summarization(
                sentiCL, event_news_list, event_tweet_list, word_dist, vectorizer, time_mu, time_sigma, topk, debug)
            news_summary.sort(key = lambda s: s.created_at)
            
            news_summary_text = ""
            for i in xrange(len(news_summary)):
                news_summary_text+=(str(news_summary[i].created_at)[:10]+'  '+news_summary[i].title+'\n\n')
            news_summary_text = news_summary_text[:-2]
            # print "news summary is"
            # print news_summary_text
            # print

            news_summary_list.append(news_summary_text)
            tweets_summary_text = '\n\n'.join(tweets_summary)
            # print "tweets summary is"
            # print tweets_summary_text
            # print
            tweets_summary_list.append(tweets_summary_text)

            opinion_percent.append((getSentiPercentage(sentiCL, tweets[:2000], tweets_rele)))

        request.session[
            prepend_date(start_str, end_str, 'top_title')] = top_title
        request.session[
            prepend_date(start_str, end_str, 'top_term_dic')] = top_term_dic
        request.session[
            prepend_date(start_str, end_str, 'news_summary_list')] = news_summary_list
        request.session[
            prepend_date(start_str, end_str, 'tweets_summary_list')] = tweets_summary_list
        request.session[
            prepend_date(start_str, end_str, 'opinion_percent')] = opinion_percent
        cur_cache = PLSACache(
            data, Pw_zs, n_wdxPz_wds, ind2obj, terms, reverse_voc, vectorizer)

        cache_file = File(
            open('./media/cache' + start_str + '_' + end_str, 'w'))
        pickle.dump(cur_cache, cache_file)
        cache_file.close()

    return HttpResponse('OK')


def event_display(request, start_str, end_str):

    top_title = request.session.get(
        prepend_date(start_str, end_str, 'top_title'), [])
    top_term_dic = request.session.get(
        prepend_date(start_str, end_str, 'top_term_dic'), [])

    news_summary_list = request.session.get(
        prepend_date(start_str, end_str, 'news_summary_list'), [])
    tweets_summary_list = request.session.get(
        prepend_date(start_str, end_str, 'tweets_summary_list'), [])

    event_info_list = []

    wordcloud_str = []

    for i in xrange(len(top_term_dic)):
        target = drawWordCloud(top_term_dic[i]).replace(
            'placeholder', '#wordcloudarea' + str(i))
        wordcloud_str.append(target)

    # for i in xrange(len(news_summary_list)):
    #     event_info_list.append(zip(top_title[i], top_term[i]))
    for i in xrange(len(news_summary_list)):
        event_info_list.append((news_summary_list[i], tweets_summary_list[i]))

    # print "heihei",event_info_list
    context = {'start_str': start_str, 'end_str': end_str,
               'event_info_list': event_info_list, 'wordcloud_str': wordcloud_str}

    return render(request, 'eventDisplay.html', context)


def aspect_running(request, start_str='19901025', end_str='19901025', event=0):

    try:
        cache_file = open('./media/cache' + start_str + '_' + end_str)
        cur_cache = pickle.load(cache_file)
        cache_file.close()

        event = int(event)
        data, n_wdxPz_wds, ind2obj, terms, reverse_voc, prev_Pw_zs, vectorizer = cur_cache.Xdata, cur_cache.n_wdxPz_wds, cur_cache.ind2obj, cur_cache.terms, cur_cache.reverse_voc, cur_cache.Pw_zs, cur_cache.vectorizer

        Xevents, dID = selectTopic(data[:numX], n_wdxPz_wds, event)

        # for each in dID:
        #     print "original title", ind2obj[each].title
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
        lambdaB = 0.6
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

            # if aspect_num_ == 1:
            #     return HttpResponse('OneError')

            inits_notime, labels_km = km_initialize(
                X, Xe, entityTypes, aspect_num_)
            mu_km, sigma_km = inittime(DTevent, aspect_num_, labels_km)
            inits = inits_notime + [mu_km, sigma_km]

            Pw_zs, Pz_d, Pd, mu, sigma, Li = pLSABet.pLSABet(
                selectTime, numX, Learn, data, inits, wt, lambdaB)
        print "pLSA done in " + str(time.time() - t0)

        # Pw_zs, Pz_d, cluster_num_ = filterEvent(Pw_zs, Pz_d, Pd)
        Pw_zs, Pz_d, mu, sigma, aspect_num_ = rankEventwithTime(Pw_zs, Pz_d, Pd, mu, sigma)


        # for each in entityTypes:
        Pw_z = Pw_zs[0]
        Pp_z = Pw_zs[1]
        Pl_z = Pw_zs[2]
        Po_z = Pw_zs[3]

        top_term_dic = find_topterms_dic(Pw_z, terms, 30)


        aspect_n_wdxPz_wds = []
        for i in xrange(numX):
            aspect_n_wdxPz_wds.append(weightX(data[i], Pw_zs[i], Pz_d))

        news_summary_list = []
        tweets_summary_list = []
        Xaspects_list = []

        event_tweet_list = []
        for each in dID:
            event_tweet_list+=list(ind2obj[each].tweet_set.all())

        aspect_opinion_percent = []
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
            for each in aspect_dID:
                # print ind2obj[ dID[each]].title
                event_news_list.append(ind2obj[ dID[each]])
                
            word_dist = Pw_z[:, aspect].T
            time_mu = mu[aspect]
            time_sigma = sigma[aspect]
            # event_tweet_list = []
            # for i in xrange(len(event_news_list)):
            #     event_tweet_list += list(event_news_list[i].tweet_set.all())
            news_summary, tweets_summary, tweets, tweets_rele, sentiment = summarization(
                sentiCL, event_news_list, event_tweet_list, word_dist, vectorizer, time_mu, time_sigma, topk, debug)
            news_summary.sort(key = lambda s: s.created_at)
            news_summary_text = ""
            for i in xrange(len(news_summary)):
                news_summary_text+=(str(news_summary[i].created_at)[:10]+'  '+news_summary[i].title+'\n\n')
            news_summary_text = news_summary_text[:-2]

            # print "news summary is"
            # print news_summary_text
            news_summary_list.append(news_summary_text)

            tweets_summary_text = '\n\n'.join(tweets_summary)
            # print "tweets summary is"
            # print tweets_summary_text
            # print
            tweets_summary_list.append(tweets_summary_text)
            aspect_opinion_percent.append((getSentiPercentage(sentiCL, tweets[:500], tweets_rele)))


        gd = EntityGraphData(0.005, event, aspect_num_, reverse_voc, prev_Pw_zs[
                             1], prev_Pw_zs[2], prev_Pw_zs[3], Xaspects_list, Pp_z, Pl_z, Po_z)

        top_title = find_toptitle_dID(Pz_d, ind2obj, topk, dID)
        top_term = find_topterms_simple(Pw_z, terms, topk)

        request.session[
            prepend_date(start_str, end_str, 'event' + str(event) + 'top_term_dic')] = top_term_dic
        request.session[prepend_date(
            start_str, end_str, 'event' + str(event) + 'top_title')] = top_title
        request.session[
            prepend_date(start_str, end_str, 'event' + str(event) + 'top_term')] = top_term
        request.session[
            prepend_date(start_str, end_str, 'event' + str(event) + 'news_summary_list')] = news_summary_list
        request.session[
            prepend_date(start_str, end_str, 'event' + str(event) + 'tweets_summary_list')] = tweets_summary_list
        request.session[
            prepend_date(start_str, end_str, 'event' + str(event) + 'aspect_opinion_percent')] = aspect_opinion_percent
        
        graphStr = textGen(gd)
        aspectGraphStr = []

        for i in xrange(aspect_num_):
            aspectGraphStr.append(
                aspectTextGen(gd, i).replace("#area1", "#aspectEntityArea" + str(i)))

        distStr = drawLineDist(aspect_num_, start_str, end_str, mu, sigma)
        graphBuffer[prepend_date(start_str, end_str, 'graph')] = graphStr
        graphBuffer[
            prepend_date(start_str, end_str, 'aspectGraph')] = aspectGraphStr
        graphBuffer[prepend_date(start_str, end_str, 'dist')] = distStr

    except IOError as e:
        print "Unable to open file"

    return HttpResponse('OK')


def aspect_display(request, start_str, end_str, event=0):

    event = int(event)

    top_title = request.session.get(
        prepend_date(start_str, end_str, 'event' + str(event) + 'top_title'), [])
    top_term = request.session.get(
        prepend_date(start_str, end_str, 'event' + str(event) + 'top_term'), [])
    # top_person = request.session.get(
    #     prepend_date(start_str, end_str, 'event' + str(event) + 'top_person'), [])
    # top_place = request.session.get(
    #     prepend_date(start_str, end_str, 'event' + str(event) + 'top_place'), [])
    # top_org = request.session.get(
    # prepend_date(start_str, end_str, 'event' + str(event) + 'top_org'), [])
    
    event_news_summary = request.session.get(
        prepend_date(start_str, end_str, 'news_summary_list'), [])[event]

    event_tweets_summary = request.session.get(
        prepend_date(start_str, end_str, 'tweets_summary_list'), [])[event]

    aspect_news_summary_list = request.session.get(
        prepend_date(start_str, end_str, 'event' + str(event) + 'news_summary_list'), [])

    aspect_tweets_summary_list = request.session.get(
        prepend_date(start_str, end_str, 'event' + str(event) + 'tweets_summary_list'), [])

    event_opinion_percent = request.session.get(prepend_date(start_str, end_str, 'opinion_percent'), [])[event]

    aspect_opinion_percent = request.session.get(prepend_date(start_str, end_str, 'event' + str(event) + 'aspect_opinion_percent'), [])

    event_top_term_dic = request.session.get(
        prepend_date(start_str, end_str, 'top_term_dic'), [])

    aspect_top_term_dic = request.session.get( prepend_date(start_str, end_str, 'event' + str(event) + 'top_term_dic'), [])

    event_wordcloud_str = drawWordCloud(event_top_term_dic[event]).replace(
        'placeholder', '#eventwordcloud')

    event_opinion_str = drawOpinionPie(event_opinion_percent).replace('placeholder', '#eventopinion')

    aspect_opinion_str = []

    for i in xrange(len(aspect_opinion_percent)):
        aspect_opinion_str.append(drawOpinionPie(aspect_opinion_percent[i]).replace('placeholder', '#aspectopinion'+str(i)))
    
    aspect_wordcloud_list = []
    for i in xrange(len(aspect_top_term_dic)):
        aspect_wordcloud_list.append( drawWordCloud(aspect_top_term_dic[i]).replace(
        'placeholder', '#aspectwordcloud'+str(i) )   )


    graphStr = graphBuffer.get(prepend_date(start_str, end_str, 'graph'), "")
    distStr = graphBuffer.get(prepend_date(start_str, end_str, 'dist'), "")
    aspectGraphStr = graphBuffer.get(
        prepend_date(start_str, end_str, 'aspectGraph'), [])
    # cache_file = open('./media/cache' + start_str + '_' + end_str)
    # cur_cache = pickle.load(cache_file)
    # cache_file.close()
    # data, terms, reverse_voc = cur_cache.Xdata,  cur_cache.terms, cur_cache.reverse_voc

    event_info_list = []

    for i in xrange(len(aspect_news_summary_list)):
        event_info_list.append(
            (aspect_news_summary_list[i], aspect_tweets_summary_list[i], colors[i]))

    context = {'start_str': start_str, 'end_str': end_str, 'event_news_summary': event_news_summary, 'event_tweets_summary': event_tweets_summary, 'event_wordcloud_str': event_wordcloud_str,
               'event_info_list': event_info_list, 'graphStr': graphStr, 'distStr': distStr, 'aspectGraphStr': aspectGraphStr, 'event_opinion_str':event_opinion_str,'aspect_opinion_str':aspect_opinion_str,'aspect_wordcloud_list':aspect_wordcloud_list}

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

    graphStr = graphBuffer.get(prepend_date(start_str, end_str, 'graph'), "")

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
               'event_info_list': event_info_list, 'graphStr': graphStr}

    return render(request, 'aspectDisplayNoAspect.html', context)


def graph_test(request):

    fig = Figure(figsize=(5, 2), dpi=100, tight_layout = True)
    canvas = FigureCanvas(fig)

    ax = fig.add_subplot(1, 1, 1)
    # Read the whole text.
    wordcloud = WordCloud(font_path='Verdana.ttf', background_color="white").generate(
        "adsf sdf w q a aa aaaaa sssss aaaass sssss sssss sssss")
    # wordcloud = WordCloud().generate(text)
    # Open a plot of the generated image.
    ax.imshow(wordcloud)
    ax.axis("off")
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)

    return response


if __name__ == '__main__':
    print parse_date('15-02-05')
