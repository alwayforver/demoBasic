# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('overviews', '0004_auto_20150317_0104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metainfo',
            name='news_end_date',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='metainfo',
            name='news_start_date',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
    ]
