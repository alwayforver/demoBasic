# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('overviews', '0004_auto_20141020_0341'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tweet',
            name='related_news',
        ),
        migrations.AlterField(
            model_name='news',
            name='related_tweet',
            field=models.ManyToManyField(to=b'overviews.Tweet'),
        ),
    ]
