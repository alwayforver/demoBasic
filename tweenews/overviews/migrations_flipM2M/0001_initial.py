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
                ('raw_text', models.CharField(max_length=2000)),
                ('key_word', models.CharField(max_length=30, blank=True)),
                ('source', models.CharField(default=b'GF', max_length=2, choices=[(b'GF', b'Google News Feed')])),
                ('created_at', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('ID', models.BigIntegerField(serialize=False, primary_key=True)),
                ('user', models.CharField(max_length=30, verbose_name=b'tweet user')),
                ('raw_text', models.CharField(max_length=2000)),
                ('created_at', models.DateTimeField()),
                ('is_retweet', models.BooleanField(default=False)),
                ('key_word', models.CharField(max_length=30, blank=True)),
                ('retweet_count', models.BigIntegerField(default=0)),
                ('hash_tags', models.CharField(default=b'', max_length=30, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='news',
            name='related_tweet',
            field=models.ManyToManyField(to='overviews.Tweet'),
            preserve_default=True,
        ),
    ]
