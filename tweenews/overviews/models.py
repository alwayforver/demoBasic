from django.db import models

# Create your models here.

class Tweet(models.Model):
    ID = models.BigIntegerField(primary_key = True)
    user = models.CharField(max_length=30, verbose_name='tweet user')
    raw_text = models.CharField(max_length=2000)
    created_at = models.DateTimeField()
    related_news = models.CharField(max_length=100, default = "", blank = True,)
    is_retweet= models.BooleanField(default = False)
    key_word = models.CharField(max_length=30,blank = True)
    retweet_count = models.BigIntegerField(default=0)
    hash_tags = models.CharField(max_length=30, blank = True, default = "")

    # def __init__(_id, _user, _raw_text, _key_word, _created_at):
    #     self.ID = _id
    #     self.user = _user
    #     self.raw_text = _raw_text
    #     self.key_word = _key_word
    #     self.created_at=_created_at

    # def __init__():
    #     super.__init__()

class News(models.Model):
    ID = models.BigIntegerField(primary_key = True)
    SOURCE_CHOICES = (("GF", "Google News Feed"),)
    raw_text = models.CharField(max_length=2000)
    key_word = models.CharField(max_length=30, blank=True)
    source = models.CharField(max_length=2, choices = SOURCE_CHOICES, default = "GF")
    created_at = models.DateTimeField()
    related_Tweets = models.CharField(max_length=100, default = "")









