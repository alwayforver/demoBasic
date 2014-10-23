# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('overviews', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='main_article',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='news',
            name='related_article',
            field=models.CharField(default=b'', max_length=200),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='news',
            name='title',
            field=models.CharField(default=b'testtitle', max_length=100),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='news',
            name='ID',
            field=models.CharField(max_length=200, serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='news',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2014, 10, 23, 20, 44, 48, 439860)),
        ),
    ]
