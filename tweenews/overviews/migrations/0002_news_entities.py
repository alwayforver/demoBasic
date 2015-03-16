# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('overviews', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='entities',
            field=models.CharField(max_length=5000, null=True, blank=True),
            preserve_default=True,
        ),
    ]
