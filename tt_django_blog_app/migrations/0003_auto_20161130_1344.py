# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-30 21:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tt_django_blog_app', '0002_auto_20161129_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='blog_date_created',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='blog',
            name='blog_date_modified',
            field=models.CharField(max_length=60),
        ),
    ]
