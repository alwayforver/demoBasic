import os
import sys
from datetime import datetime
import django
import re
import string

local_base = '~/projects/demoBasic/tweenews'
sys.path.append(local_base)

os.environ['DJANGO_SETTINGS_MODULE']='tweenews.settings'

from overviews.models import News, Tweet

def try_utf8(data):
    "Returns a Unicode object on success, or None on failure"
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return None


# test git
# This is a script for database queries
# Please refer to https://docs.djangoproject.com/en/dev/topics/db/queries/
if __name__ == "__main__":
    if len(sys.argv) != 3:
	print 'usage: python ' + sys.argv[0] + ' newsfile tweetfolder'
	sys.exit(-1)
    django.setup()
    
    
    # save news
    # for each news in news.txt, save news
    #     for each related tweets:
    ##        save tweets and add related news
    f = open(sys.argv[1],"r")
    fmt = "%a, %d %b %Y %H:%M:%S"
    news_log = open("news.log","a+")
    tweets_log = open("tweets.log","a+")
    for line in f:
        if len(line.strip().split("\t")) != 8:
            continue
        url,title,source,date,authors,keywords,snippets,text = line.strip().split("\t")
        date = re.sub(" [\+\-]\d{4}","",date)
        date = datetime.strptime(date,fmt)
        
        if len(text) > 10000:
            text = text[:10000]
	    news_log.write("text too long: "+title+"\t"+text+"\n")
        if len(title) > 200:
            title = title[:200]
	    news_log.write("title too long: "+title+"\t"+text+"\n")
        if len(keywords) > 200:
            keywords = keywords[:200]
	    news_log.write("keywords too long: "+title+"\t"+text+"\n")
        if try_utf8(text) is None:
            news_log.write(title+"\t"+text+"\n")
            continue
        news = News(url = url, raw_text = text,created_at = date, key_word = keywords, source = source, title = title)
	#print title
        news.save()
        ID = news.id

        # for each related tweets
        #t_path = os.path.join("/srv/data/twitter_news/data/tweets/",title.translate(string.maketrans("",""), string.punctuation).replace(" ","_") + '-' + source.replace(" ","_"))
        #t_path = os.path.join("/srv/data/twitter_news/data/tweets/",title.replace(" ","_") + '-' + source.replace(" ","_"))
#        t_path = os.path.join(sys.argv[2],title.replace(" ","_") + '-' + source.replace(" ","_"))
        t_path = os.path.join(sys.argv[2],("".join(c for c in title if c not in (string.punctuation))).replace(' ', '_') + '-' + ("".join(c for c in source if c not in (string.punctuation))).replace(' ', '_'))
        if os.path.exists(t_path):
            t = open(t_path,"r")
        else:
            continue
        fmt1 = "%a %b %d %H:%M:%S %Y"
        counter = 0
        for line in t:
	    fields = line.strip().split("\t")
            if len(fields) != 27:  # new format of the crawled tweets
        	#print "27"
		tweets_log.write("not 27:"+line.strip()+"\n")
		continue

            tw_id_str, tw_text, tw_created_at, contained_url, tag_text, retw_id_str, retw_favorited, retw_favorite_count, retw_retweeted, retw_retweet_count, \
            tw_favorited, tw_favorite_count, tw_retweeted, tw_retweet_count, user_id_str, verified, follower_count, statuses_count, friends_count, \
	    favorites_count, user_created_at= fields[:21]
            
            # convert user_created time
            tw_created_at = re.sub("[\+\-]\d{4} ","",tw_created_at)
            tw_created_at = datetime.strptime(tw_created_at,fmt1)
            
            if try_utf8(tw_text) is None:
                tweets_log.write(tw_id_str +"\t"+tw_text+"\n")
                continue

            # tw_text = re.sub(r'[\U00010000-\U0010ffff]','',tw_text)
            
            # Tweet object
            
            tweet = Tweet(ID=int(tw_id_str), user=int(user_id_str) ,raw_text = tw_text,created_at = tw_created_at, retweet_count = tw_retweet_count,\
            hash_tags = tag_text)
	    #print tw_text
	    #print tw_id_str
            tweet.save() # save the record into django db
            tweet.related_news.add(news)
        t.close()
    news_log.close()
    tweets_log.close()
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
    
    





