# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('principal', '0004_auto_20150415_2006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empresa',
            name='abr',
            field=models.CharField(unique=True, max_length=3),
        ),
        migrations.AlterField(
            model_name='empresa',
            name='empresa',
            field=models.CharField(unique=True, max_length=100),
        ),
    ]
