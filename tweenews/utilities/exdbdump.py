import os
import sys
from datetime import datetime
import django


local_base = '/Users/Min/Dropbox/Lab/TweeNews/demoBasic/tweenews'
sys.path.append(local_base)

os.environ['DJANGO_SETTINGS_MODULE']='tweenews.settings'

from overviews.models import News, Tweet


if __name__ == "__main__":
    django.setup()
    for i in range(3):
        tweet = Tweet(ID=i, user="user"+str(i),
                        raw_text = "this is a test tweet",created_at=datetime.now(), key_word="test,test",hash_tags="")
        tweet.save()