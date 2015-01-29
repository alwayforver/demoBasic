from django.db import models
from datetime import datetime
# Create your models here.

class News(models.Model):
    ID = models.BigIntegerField(primary_key = True)
    #ID = models.CharField(max_length=200,primary_key = True)
    #SOURCE_CHOICES = (("GF", "Google News Feed"),)
    raw_text = models.CharField(max_length=10000)
    key_word = models.CharField(max_length=200, blank=True)
    source = models.CharField(max_length=30,default="GF")
   # source = models.CharField(max_length=2, choices = SOURCE_CHOICES, default = "GF")
    #created_at = models.DateTimeField(default = datetime(2014, 1, 1, 1, 1, 1))
    created_at = models.DateTimeField()
    local_time_zone = models.CharField(max_length = 20)
    title = models.CharField(max_length=200,default="testtitle")
    main_article = models.BooleanField(default=True)
    related_article = models.CharField(max_length=200,default="")
    url = models.CharField(max_length=200)

    def __str__(self):
        return "News "+str(self.ID)


class Tweet(models.Model):
    ID = models.BigIntegerField(primary_key = True)
    #user = models.CharField(max_length=30, verbose_name='tweet user')
    user = models.BigIntegerField(verbose_name='tweet user')
    raw_text = models.CharField(max_length=200)
    created_at = models.DateTimeField()
    local_time_zone = models.CharField(max_length = 20)
    is_retweet= models.BooleanField(default = False)
#    key_word = models.CharField(max_length=30,blank = True)
    retweet_count = models.BigIntegerField(default=0)
    hash_tags = models.CharField(max_length=100, blank = True, default = "")
    related_news = models.ManyToManyField(News)

    def __str__(self):
	return "Tweet "+str(self.ID)+ ' '  + str(self.raw_text.encode("utf-8","ignore"))











