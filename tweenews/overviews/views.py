from django.shortcuts import render
from django.http import HttpResponse
from overviews.models import News, Tweet

def index(request):
    
    return render(request,"index.html")

def news(request):
    all_news_list = News.objects.all()

    context = {'all_news_list':all_news_list}
    return render(request, 'news.html', context)

def tweet_with_news(request, news_ID):
    related_tweets_list = Tweet.objects.filter(related_news=news_ID)
    context = {'related_tweets_list':related_tweets_list}
    return render(request, 'relatedTweets.html', context)







