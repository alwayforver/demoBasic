# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('raw_text', models.CharField(max_length=15000)),
                ('key_word', models.CharField(max_length=200, blank=True)),
                ('source', models.CharField(default=b'GF', max_length=30)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2014, 1, 1, 1, 1, 1))),
                ('title', models.CharField(default=b'testtitle', max_length=200)),
                ('main_article', models.BooleanField(default=True)),
                ('related_article', models.CharField(default=b'', max_length=200)),
                ('url', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('ID', models.BigIntegerField(serialize=False, primary_key=True)),
                ('user', models.BigIntegerField(verbose_name=b'tweet user')),
                ('raw_text', models.CharField(max_length=150)),
                ('created_at', models.DateTimeField()),
                ('is_retweet', models.BooleanField(default=False)),
                ('retweet_count', models.BigIntegerField(default=0)),
                ('hash_tags', models.CharField(default=b'', max_length=100, blank=True)),
                ('related_news', models.ManyToManyField(to='overviews.News')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
