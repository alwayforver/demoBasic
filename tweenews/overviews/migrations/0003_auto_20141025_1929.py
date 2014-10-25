# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('overviews', '0002_auto_20141025_1925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2014, 10, 25, 19, 29, 23, 771800)),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='hash_tags',
            field=models.CharField(default=b'', max_length=100, blank=True),
        ),
    ]
