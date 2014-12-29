from django.shortcuts import render, render_to_response
from django.http import HttpResponse, Http404
from overviews.models import News, Tweet
import math
import time
from overviews.forms import SearchForm

def index(request):
    
    return render(request,"index.html")

def tweet_with_news(request, news_ID, pos = 1, counts = -1):
    base_page = 1
    pos = max(int(pos),base_page)
    one_page = 30
    default_pagenum = 10
    start = time.time()
    try:
        current_news = News.objects.get(pk=news_ID)
    except:
        raise Http404
    if counts == -1:
        #counts = Tweet.objects.filter(related_news=news_ID).count()
        counts = current_news.tweet_set.all().count()

    total_num = counts

    related_tweets_list = News.objects.get(ID=news_ID).tweet_set.all()[(pos-1)*one_page : pos*one_page]
    #related_tweets_list = Tweet.objects.filter(related_news=news_ID)[(pos-1)*one_page : pos*one_page]
    end_pos = min( pos + default_pagenum , int(math.ceil(float(total_num)/float(one_page))))
    end_pos = max( pos , end_pos)
    last_pos = int(math.ceil(float(total_num)/float(one_page)))
    
    page_index = range(pos, end_pos+1)
    prev = max(1, pos - 1)
    nextPos = min(end_pos, pos+1)
    context = {'related_tweets_list':related_tweets_list,'current_news':current_news, 'nextPos': nextPos,'prevPos': prev, 'page_index':page_index, 'counts':total_num, 'last_pos': last_pos}
    return render(request, 'relatedTweets.html', context)

def tweet_page(request, tweet_id):
	res_tweet = Tweet.objects.get(ID = tweet_id)
	context = {'tweet': res_tweet}
	return render(request, 'tweet_basic.html', context)


def cluster_view(request):
    context = {}
    return render(request, 'cluster.html', context)









