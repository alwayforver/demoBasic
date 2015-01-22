from django.db import models
from datetime import datetime
# Create your models here.

class News(models.Model):
    news_id = models.BigIntegerField(primary_key = True)
    news_url = models.CharField(max_length = 300, null = True, blank = True)
    news_title = models.CharField(max_length = 200, null = True, blank = True)
    news_source = models.CharField(max_length = 50, null = True, blank = True)
    news_date = models.DateTimeField(null = True)
    news_authors = models.CharField(max_length = 300, null = True, blank = True)
    news_keywords = models.CharField(max_length = 200, null = True, blank = True)
    news_snippets = models.CharField(max_length = 500, null = True, blank = True)
    news_content = models.CharField(max_length = 20000, null = True, blank = True)

    main_article = models.NullBooleanField(default=True, null = True)
    related_article = models.CharField(max_length=200,default="", null = True, blank = True)

    def __str__(self):
        return "News "+str(self.ID)


class Tweet(models.Model):

    tweet_id = models.BigIntegerField(primary_key = True)
    tweet_text = models.CharField(max_length = 200, null = True, blank = True)
    tweet_time = models.DateTimeField(null = True)
    tweet_urls = models.CharField(max_length = 100, null = True, blank = True)
    tweet_hashtags = models.CharField(max_length = 50, null = True, blank = True)
    retweet_id = models.BigIntegerField(null = True)
    retweet_favorited = models.NullBooleanField(default = False)
    retweet_favorite_count = models.IntegerField(null = True)
    retweet_retweeted = models.NullBooleanField(default = False)
    retweet_retweet_count = models.IntegerField(null = True)
    tweet_favorited = models.NullBooleanField(default = False)
    tweet_favorite_count = models.IntegerField(null = True)
    tweet_retweeted = models.NullBooleanField(default = False)
    tweet_retweet_count = models.IntegerField(null = True)
    user_id = models.BigIntegerField(null = True)
    user_verified = models.NullBooleanField(default = False)
    user_followers_count = models.IntegerField(null = True)
    user_status_count = models.IntegerField(null = True)
    user_friends_count = models.IntegerField(null = True)
    user_favorites_count = models.IntegerField(null = True)
    user_created_time = models.DateTimeField(null = True)
    user_location = models.CharField(max_length = 100, null = True, blank = True)
    tweet_coordinates = models.CharField(max_length = 40, null = True, blank = True)
    tweet_source = models.CharField(max_length = 30, null = True, blank = True)
    tweet_mentions = models.CharField(max_length = 100, null = True, blank = True)
    tweet_reply_user_id = models.BigIntegerField(null = True)
    tweet_reply_status_id = models.BigIntegerField(null = True)

    related_news = models.ManyToManyField(News)

    def __str__(self):
	return "Tweet "+str(self.ID)+ ' '  + str(self.raw_text.encode("utf-8","ignore"))











