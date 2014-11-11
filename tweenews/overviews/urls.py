from django.conf.urls import patterns, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from overviews import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    # url(r'^admin)
    url(r'^news/$', views.news, name='news_home'),
    url(r'^news/page(?P<pos>\d+)rank:(?P<rank_method>\d+)$', views.news, name='news_next'),
    url(r'^tweet/id=(?P<tweet_id>\d+)/$', views.tweet_page, name='tweet_base'),
    url(r'^tweet/news=(?P<news_ID>\d+)/$',views.tweet_with_news, name ='tweet_with_news'),
)
urlpatterns += staticfiles_urlpatterns()