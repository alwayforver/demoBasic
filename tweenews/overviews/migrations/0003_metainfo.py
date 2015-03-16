# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('overviews', '0002_news_entities'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetaInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('news_start_date', models.DateField()),
                ('new_end_date', models.DateField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
