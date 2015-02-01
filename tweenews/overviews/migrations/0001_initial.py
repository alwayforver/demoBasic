# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('ID', models.BigIntegerField(serialize=False, primary_key=True)),
                ('url', models.CharField(max_length=300, null=True, blank=True)),
                ('title', models.CharField(max_length=200, null=True, blank=True)),
                ('source', models.CharField(max_length=50, null=True, blank=True)),
                ('created_at', models.DateTimeField(null=True)),
                ('authors', models.CharField(max_length=300, null=True, blank=True)),
                ('key_word', models.CharField(max_length=200, null=True, blank=True)),
                ('snippet', models.CharField(max_length=500, null=True, blank=True)),
                ('raw_text', models.CharField(max_length=10000, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('ID', models.BigIntegerField(serialize=False, primary_key=True)),
                ('raw_text', models.CharField(max_length=200, null=True, blank=True)),
                ('created_at', models.DateTimeField(null=True)),
                ('tweet_urls', models.CharField(max_length=100, null=True, blank=True)),
                ('hash_tags', models.CharField(max_length=50, null=True, blank=True)),
                ('retweet_id', models.BigIntegerField(null=True)),
                ('retweet_is_favorited', models.NullBooleanField(default=False)),
                ('retweet_favorite_count', models.IntegerField(null=True)),
                ('retweet_is_retweeted', models.NullBooleanField(default=False)),
                ('retweet_retweet_count', models.IntegerField(null=True)),
                ('is_favorited', models.NullBooleanField(default=False)),
                ('favorite_count', models.IntegerField(null=True)),
                ('is_retweet', models.NullBooleanField(default=False)),
                ('retweet_count', models.IntegerField(null=True)),
                ('user', models.BigIntegerField(null=True)),
                ('verified', models.NullBooleanField(default=False)),
                ('followers_count', models.IntegerField(null=True)),
                ('status_count', models.IntegerField(null=True)),
                ('friends_count', models.IntegerField(null=True)),
                ('user_favorites_count', models.IntegerField(null=True)),
                ('user_created_at', models.DateTimeField(null=True)),
                ('location', models.CharField(max_length=100, null=True, blank=True)),
                ('coordinates', models.CharField(max_length=40, null=True, blank=True)),
                ('source', models.CharField(max_length=30, null=True, blank=True)),
                ('mentions', models.CharField(max_length=100, null=True, blank=True)),
                ('reply_user_id', models.BigIntegerField(null=True)),
                ('reply_status_id', models.BigIntegerField(null=True)),
                ('related_news', models.ManyToManyField(to='overviews.News')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
