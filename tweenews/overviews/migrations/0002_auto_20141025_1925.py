# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('overviews', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2014, 10, 25, 19, 25, 7, 76873)),
        ),
        migrations.AlterField(
            model_name='news',
            name='key_word',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='news',
            name='raw_text',
            field=models.CharField(max_length=20000),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='raw_text',
            field=models.CharField(max_length=150),
        ),
    ]
