# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('overviews', '0003_auto_20141018_2223'),
    ]

    operations = [
        migrations.RenameField(
            model_name='news',
            old_name='related_Tweets',
            new_name='related_tweet',
        ),
    ]
