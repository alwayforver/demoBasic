from django.shortcuts import render
import sys
import os
import os.path
from django.http import HttpResponse
from overviews.models import News, Tweet, MetaInfo
import time
from datetime import datetime, timedelta
from django.utils import timezone
# from django.views.decorators.csrf import csrf_exempt
# from scipy.sparse import csr_matrix
# from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pickle
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# from matplotlib.figure import Figure
# from wordcloud import WordCloud


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from django.core.files import File
sys.path.insert(0, os.path.join(BASE_DIR, 'lib'))
from k_means import km_initialize
import pLSABet
from utility import news_initialization, calc_cluster_num,filterEventKeyword, rankEventwithTime, filterEvent, find_topterms_dic, find_toptitle_dID, PLSACache, array2csr_matrix, csr_matrix2array, selectTopic, weightX, get_ticks, data_prep, parse_date, prepend_date, find_toptitle_simple, find_topterms_simple, calc_entity_matrix, inittime
from GraphData import drawOpinionPie, drawWordCloud, dataTextGen, aspectTextGen, EntityGraphData, textGen, drawLineDist
from tweetAnalysis import getSentiPercentage, LRSentiClassifier
from summarization import summarization


# from django.core.contex_processors import csrf

debug = True

all_start = timezone.make_aware(
    datetime(2014, 12, 31, 23, 23, 47), timezone.get_default_timezone())
all_end = timezone.make_aware(
    datetime(2015, 1, 4, 5, 44, 17), timezone.get_default_timezone())

cluster_num = 20
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

    cluster_num = calc_cluster_num(start_date, end_date)

    print "num of cluster is", cluster_num

    # dealing with keywords
    if len(keywords)==0:
        keywords = []
    else:
        keywords = keywords.strip().split(',')
    keywords = [keyword.strip().lower() for keyword in keywords]

    
    # if os.path.exists('./media/cache' + start_str + '_' + end_str) and prepend_date(start_str, end_str, 'top_title') in request.session:
    #     print "exist!"
    # for test use, later will change to test cache existence
    if True:
        all_news = News.objects.filter(
            created_at__gte=start_date).filter(created_at__lte=end_date)

        # print 'all_news',time.time()-t0
        # t0 = time.time()

        # Vectorizor and raw data preparation
        entityTypes = ['person', 'place', 'org']

        news_title, news_entities, news_DT, ind2obj, vectorizer, X, terms, Xe, reverse_voc, data = news_initialization(all_news, entityTypes)

        # run PLSA
        t0 = time.time()
        Learn = (1, 20)
        selectTime = 1
        wt = 0.5
        lambdaB = 0.2

        Pw_zs, Pz_d, Pd, mu, sigma, Li, cluster_num_  = pLSABet.pLSAWrapper(selectTime, numX, Learn, data, wt, lambdaB, debug, X, Xe, news_DT, entityTypes, cluster_num)

        print "pLSA done in " + str(time.time() - t0)

        # for cluster quality evaluation
        # Pw_zs, Pz_d, mu, sigma, cluster_num_ = filterEvent(Pw_zs, Pz_d, Pd, mu, sigma)
        if len(keywords) != 0:
            Pw_zs, Pz_d, mu, sigma, cluster_num_ = filterEventKeyword(Pw_zs, Pz_d, Pd, mu, sigma, terms, keywords)

        # top_title = find_toptitle_simple(Pz_d, ind2obj, topk)
        top_term_dic = find_topterms_dic(Pw_zs[0], terms, 30)

        n_wdxPz_wds = []
        for i in range(numX):
            n_wdxPz_wds.append(weightX(data[i], Pw_zs[i], Pz_d))

        news_summary_list = []
        tweets_summary_list = []
        opinion_percent = []

        for event in xrange(cluster_num_):
            print "##################### Event", event, "#################"
            print
            _, dID = selectTopic(data[:numX], n_wdxPz_wds, event)
            print 'select topic',time.time()-t0
            t0 = time.time()
            event_news_list = []
            for each in dID:
                event_news_list.append(ind2obj[each])
            word_dist = Pw_zs[0][:, event].T
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

            news_summary_list.append(news_summary_text)
            tweets_summary_text = '\n\n'.join([t.raw_text for t in tweets_summary])
            tweets_summary_list.append(tweets_summary_text)

            opinion_percent.append((getSentiPercentage(sentiCL, tweets[:2000], tweets_rele)))

        # request.session[
        #     prepend_date(start_str, end_str, 'top_title')] = top_title
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

    # top_title = request.session.get(
    #     prepend_date(start_str, end_str, 'top_title'), [])
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

    for i in xrange(len(news_summary_list)):
        event_info_list.append((news_summary_list[i], tweets_summary_list[i]))

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
        
        print "in aspect", n_wdxPz_wds[0],n_wdxPz_wds[1]
        Xevents, dID = selectTopic(data[:numX], n_wdxPz_wds, event)

        DT = data[-1]
        DTevent = np.array(DT)[dID]

        data = Xevents + [DTevent]
        X = data[0]
        entityTypes = ['person', 'place', 'org']

        Xe = {}
        for i in xrange(len(entityTypes)):
            Xe[entityTypes[i]] = data[i + 1]
        # for each in dID:
        #     print "original title", ind2obj[each].title
        # print "dID", len(dID)

        # run PLSA
        t0 = time.time()

        Learn = (1, 10)
        selectTime = 1
        wt = 0.5
        lambdaB = 0.6

        Pw_zs, Pz_d, Pd, mu, sigma, Li, aspect_num_  = pLSABet.pLSAWrapper(selectTime, numX, Learn, data, wt, lambdaB, debug, X, Xe, DTevent, entityTypes, aspect_num)

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
            news_summary_list.append(news_summary_text)
            tweets_summary_text = '\n\n'.join([t.raw_text for t in tweets_summary])
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

def change_settings(request):

    pass

# def graph_test(request):

#     fig = Figure(figsize=(5, 2), dpi=100, tight_layout = True)
#     canvas = FigureCanvas(fig)

#     ax = fig.add_subplot(1, 1, 1)
#     # Read the whole text.
#     wordcloud = WordCloud(font_path='Verdana.ttf', background_color="white").generate(
#         "adsf sdf w q a aa aaaaa sssss aaaass sssss sssss sssss")
#     # wordcloud = WordCloud().generate(text)
#     # Open a plot of the generated image.
#     ax.imshow(wordcloud)
#     ax.axis("off")
#     response = HttpResponse(content_type='image/png')
#     canvas.print_png(response)

#     return response


if __name__ == '__main__':
    print parse_date('15-02-05')
