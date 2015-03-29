from django.conf.urls import patterns, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from overviews import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    # url(r'^admin)
    url(r'^news/$', views.news, name='news_home'),
    url(r'^news/page(?P<pos>\d+)rank:(?P<rank_method>\d+)$', views.news, name='news_next'),
    #url(r'^news/page(?P<pos>\d+)rank:(?P<rank_method>\d+)&q=(?P<q>\w*)$', views.news, name='news_next'),
    url(r'^tweet/id=(?P<tweet_id>\d+)/$', views.tweet_page, name='tweet_base'),
    url(r'^tweet/news=(?P<news_ID>\d+)/$',views.tweet_with_news, name ='tweet_with_news'),
    #url(r'^tweet/news=(?P<news_ID>\d+)page(?P<pos>\d+):(?P<counts>\d+)&q=(?P<q>\w*)$',views.tweet_with_news, name ='tweet_with_news'),
    url(r'^tweet/news=(?P<news_ID>\d+)page(?P<pos>\d+):(?P<counts>\d+)&(?P<showURL>\d+)$',views.tweet_with_news, name ='tweet_filter'),
    url(r'^tweet/news=(?P<news_ID>\d+)page(?P<pos>\d+):(?P<counts>\d+)$', views.tweet_with_news, name='tweet_next'),
    url(r'^cluster_test/$', views.cluster_view, name='cluster_test'),
    url(r'^graph_test/$', views.graph_test, name='graph_test'),

    url(r'^event_discovery/$', views.event_view, name = 'event_discovery'),
    url(r'^event_running/start_str=(?P<start_str>\d+)end_str=(?P<end_str>\d+)/$', views.event_running, name = 'event_running'),

    url(r'^aspect_running/start_str=(?P<start_str>\d+)end_str=(?P<end_str>\d+)event=(?P<event>\d+)/$', views.aspect_running, name = 'aspect_running'),

    # url(r'^aspect_discovery/start_str=(?P<start_str>\d+)end_str=(?P<end_str>\d+)event=(?P<event>\d+)/$', views.aspect_discovery, name = 'aspect_discovery'),

    # url(r'^event_running/$', views.event_running, name = 'event_running'),

    # url(r'^event_display/$', views.event_display, name = 'event_display'),
    url(r'^event_display/start_str=(?P<start_str>\d+)end_str=(?P<end_str>\d+)/$', views.event_display, name = 'event_display'),
    url(r'^aspect_display/start_str=(?P<start_str>\d+)end_str=(?P<end_str>\d+)event=(?P<event>\d+)/$', views.aspect_display, name = 'aspect_display'),
    url(r'^aspect_display_noaspect/start_str=(?P<start_str>\d+)end_str=(?P<end_str>\d+)event=(?P<event>\d+)/$', views.aspect_display_noaspect, name = 'aspect_display_noaspect'),

    # url(r'^event_display/$', views.event_display, name = 'event_display'),



)
urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$',
            'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, }),
    )
