# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('overviews', '0002_auto_20141018_1953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='hash_tags',
            field=models.CharField(default=b'', max_length=30, blank=True),
        ),
    ]
