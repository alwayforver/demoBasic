from django.db import models

# Create your models here.

class News(models.Model):
    ID = models.BigIntegerField(primary_key = True)
    SOURCE_CHOICES = (("GF", "Google News Feed"),)
    raw_text = models.CharField(max_length=2000)
    key_word = models.CharField(max_length=30, blank=True)
    source = models.CharField(max_length=2, choices = SOURCE_CHOICES, default = "GF")
    created_at = models.DateTimeField()
    # related_tweet = models.ManyToManyField(Tweet)

    def __str__(self):
        return "News "+str(self.ID)


class Tweet(models.Model):
    ID = models.BigIntegerField(primary_key = True)
    user = models.CharField(max_length=30, verbose_name='tweet user')
    raw_text = models.CharField(max_length=2000)
    created_at = models.DateTimeField()
    is_retweet= models.BooleanField(default = False)
    key_word = models.CharField(max_length=30,blank = True)
    retweet_count = models.BigIntegerField(default=0)
    hash_tags = models.CharField(max_length=30, blank = True, default = "")
    related_news = models.ManyToManyField(News)

    def __str__(self):
        return "Tweet "+str(self.ID)











