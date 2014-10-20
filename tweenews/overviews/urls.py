from django.conf.urls import patterns, url

from overviews import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    # url(r'^admin)
    url(r'^news/$', views.news),
    url(r'^tweet/(?P<news_ID>\d+)/$',views.tweet_with_news, name ='tweet_with_news'),
)