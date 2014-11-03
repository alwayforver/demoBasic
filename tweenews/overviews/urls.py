from django.conf.urls import patterns, url
from django.conf import settings
from overviews import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    # url(r'^admin)
    url(r'^news/$', views.news, name='news_home'),
    url(r'^tweet/(?P<news_ID>\d+)/$',views.tweet_with_news, name ='tweet_with_news'),
)