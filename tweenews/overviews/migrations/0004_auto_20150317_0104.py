# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('overviews', '0003_metainfo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='metainfo',
            old_name='new_end_date',
            new_name='news_end_date',
        ),
    ]
