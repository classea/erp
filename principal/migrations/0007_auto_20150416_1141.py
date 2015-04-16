# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.hashers import make_password

from django.db import migrations


def create_superuser(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    User = apps.get_model("auth", "User")
    try:
        u = User.objects.get(username='erp')
    except User.DoesNotExists:
        password = make_password('erp')
        User(username='erp', first_name='Erp', email='erp@peixesclassea.com.br', password=password).save()


class Migration(migrations.Migration):
    dependencies = [
        ('principal', '0006_auto_20150416_1102'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
