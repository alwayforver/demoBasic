from django.db import models
from datetime import datetime
# Create your models here.

class News(models.Model):
    #ID = models.BigIntegerField(primary_key = True)
    #ID = models.CharField(max_length=200,primary_key = True)
    #SOURCE_CHOICES = (("GF", "Google News Feed"),)
    raw_text = models.CharField(max_length=20000)
    key_word = models.CharField(max_length=100, blank=True)
    source = models.CharField(max_length=30,default="GF")
   # source = models.CharField(max_length=2, choices = SOURCE_CHOICES, default = "GF")
    created_at = models.DateTimeField(default = datetime.now())
    title = models.CharField(max_length=100,default="testtitle")
    main_article = models.BooleanField(default=True)
    related_article = models.CharField(max_length=200,default="")
    url = models.CharField(max_length=200)
    # related_tweet = models.ManyToManyField(Tweet)

    def __str__(self):
        return "News "+str(self.id)


class Tweet(models.Model):
    ID = models.BigIntegerField(primary_key = True)
    user = models.CharField(max_length=30, verbose_name='tweet user')
    raw_text = models.CharField(max_length=150)
    created_at = models.DateTimeField()
    is_retweet= models.BooleanField(default = False)
    key_word = models.CharField(max_length=30,blank = True)
    retweet_count = models.BigIntegerField(default=0)
    hash_tags = models.CharField(max_length=100, blank = True, default = "")
    related_news = models.ManyToManyField(News)

    def __str__(self):
        return "Tweet "+str(self.id)











