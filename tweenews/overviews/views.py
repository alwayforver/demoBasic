from django.shortcuts import render
from django.http import HttpResponse
from overviews.models import News, Tweet
import math

def index(request):
    
    return render(request,"index.html")

def news(request, pos = 1, rank_method = 0):
    base_pk = 1

    pos = max(int(pos),base_pk)
    rank_method = int(rank_method)
    total_num = News.objects.count()
    one_page = 100
    default_pagenum = 10
    end_pos = min( pos + default_pagenum , int(math.ceil(total_num/one_page))) 
    print total_num, pos, end_pos
    if rank_method == 0:
        all_news_list = News.objects.filter(id__range = ((pos-1)*one_page+1, pos*one_page))
    elif rank_method == 1:
        all_news_list = News.objects.all().order_by('created_at')[(pos-1)*one_page : pos*one_page]
    elif rank_method == 2:
        all_news_list = News.objects.all().order_by('-created_at')[(pos-1)*one_page : pos*one_page]
    page_index = range(pos, end_pos+1)

    #all_news_list = News.objects.all()
    
    prev = max(1, pos - 1)
    nextPos = min(end_pos, pos+1)
    context = {'all_news_list':all_news_list, 'page_index':page_index, 'nextPos': nextPos,'prevPos': prev, 'rankmethod': rank_method,}
    return render(request, 'news.html', context)

def tweet_with_news(request, news_ID):
    related_tweets_list = Tweet.objects.filter(related_news=news_ID)
    current_news = News.objects.get(pk=news_ID)
    context = {'related_tweets_list':related_tweets_list,'current_news':current_news}
    return render(request, 'relatedTweets.html', context)

def tweet_page(request, tweet_id):
	res_tweet = Tweet.objects.get(ID = tweet_id)
	context = {'tweet': res_tweet}
	return render(request, 'tweet_basic.html', context)








