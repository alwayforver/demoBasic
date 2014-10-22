# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('overviews', '0002_news_title'),
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
    ]
