# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-03-22 14:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rg_instructor_analytics_log_collector', '0014_auto_20190322_1050'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='logtable',
            unique_together=set([('message_type_hash', 'log_time', 'user_name')]),
        ),
        migrations.AlterField(
            model_name='logtable',
            name='message_type',
            field=models.TextField(),
        ),
    ]
