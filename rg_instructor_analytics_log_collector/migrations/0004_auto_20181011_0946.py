# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-11 13:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rg_instructor_analytics_log_collector', '0003_auto_20180921_0525'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='enrollmentbyday',
            unique_together=set([]),
        ),
    ]