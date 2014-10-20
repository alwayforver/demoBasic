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
    #                     raw_text = "this is a test tweet",created_at=datetime.now(), key_word="test,test",hash_tags="")
    #     tweet.save()


    # for i in range(2):
    #     news = News(ID = i, raw_text = "this is a test news", created_at = datetime.now(), key_word = "test,test",)
    #     news.save()

    # get object
    tweet0 = Tweet.objects.get(pk=0)
    tweet1 = Tweet.objects.get(pk=1)
    tweet2 = Tweet.objects.get(pk=2)

    news0 = News.objects.get(pk=0)
    news1 = News.objects.get(pk=1)

    # link tweet and news

    # news0.related_tweet.add(tweet0,tweet1)
    # news1.related_tweet.add(tweet2)
    
    print Tweet.objects.filter(news__ID=0)
    





