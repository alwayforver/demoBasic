import os
import sys
from datetime import datetime
import django


local_base = '/Users/Min/Dropbox/Lab/TweeNews/demoBasic/tweenews'
sys.path.append(local_base)

os.environ['DJANGO_SETTINGS_MODULE']='tweenews.settings'

from overviews.models import News, Tweet

# This is a script for database queries
# Please refer to https://docs.djangoproject.com/en/dev/topics/db/queries/
if __name__ == "__main__":
    django.setup()

    # insert object

    # for i in range(3):
    #     tweet = Tweet(ID=i, user="user"+str(i),
    #                     raw_text = "this is test tweet "+str(i),created_at=datetime.now(), key_word="test,test",hash_tags="")
    #     tweet.save()


    # for i in range(2):
    #     news = News(ID = i, raw_text = "this is test news "+str(i), created_at = datetime.now(), key_word = "test,test",)
    #     news.save()

    # get object
    # tweet0 = Tweet.objects.get(pk=0)
    # tweet1 = Tweet.objects.get(pk=1)
    # tweet2 = Tweet.objects.get(pk=2)

    # news0 = News.objects.get(pk=0)
    # news1 = News.objects.get(pk=1)

    # link tweet and news

    # tweet0.related_news.add(news0)
    # tweet1.related_news.add(news0)
    # tweet2.related_news.add(news1)

    # acess to the relation
    # Tweet.objects.filter(related_news=0)
    # tweet0.related_news.all()
    
    





