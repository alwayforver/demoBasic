import os
import sys
from datetime import datetime
import django
import re
from warnings import filterwarnings

local_base = '~/projects/demoBasic/tweenews'
sys.path.append(local_base)

os.environ['DJANGO_SETTINGS_MODULE']='tweenews.settings'

from overviews.models import News, Tweet
# test git
# This is a script for database queries
# Please refer to https://docs.djangoproject.com/en/dev/topics/db/queries/
if __name__ == "__main__":
    django.setup()
    
    
    
    # save news
    f = open("utilities/data/news.txt","r")
    
    fmt = "%a, %d %b %Y %H:%M:%S"
    for line in f:
        url,title,source,date,authors,keywords,snippets,text = line.strip().split("\t")
        date = re.sub(" [\+\-]\d{4}","",date)

        date = datetime.strptime(date,fmt)
        news = News(ID = url, raw_text = text,created_at = date, key_word = keywords, source = source)# SOURCE_CHOICES is not in DB
        news.save()
    f.close()

    
    
    
    rootdir = "utilities/data/tweets"
    counter = 0
    for name in os.listdir(rootdir):
        
        f = open(os.path.join(rootdir,name),"r")
    # insert object
    #with open("utilities/data/tweets/Breaking_Bad_Action_Figures-TIME","r") as f:
        if os.path.getsize(os.path.join(rootdir,name)) > 0:
            fmt = "%a %b %d %H:%M:%S %Y"
            for line in f:
                counter += 1
                tw_id_str, tw_text, tw_created_at, contained_url, tag_text, retw_id_str, retw_favorited, retw_favorite_count, retw_retweeted, retw_retweet_count, \
                tw_favorited, tw_favorite_count, tw_retweeted, tw_retweet_count, user_id_str, verified, follower_count, statuses_count, friends_count, \
                favorites_count, user_created_at= line.strip().split("\t")
                print "COUNTER",counter,"XX",tag_text,"XX","\n"
                # convert user_created time
                tw_created_at = re.sub("[\+\-]\d{4} ","",tw_created_at)
                tw_created_at = datetime.strptime(tw_created_at,fmt)
            
                # Tweet object
                tweet = Tweet(ID=tw_id_str, user=user_id_str ,raw_text = tw_text,created_at = tw_created_at, key_word="test,test", retweet_count = tw_retweet_count,\
                hash_tags = tag_text)
            
                tweet.save() # save the record into django db
            f.close()
    
        
    
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
    
    





