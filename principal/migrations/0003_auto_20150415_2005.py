# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('principal', '0002_empresaativa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empresa',
            name='operador_caixa',
            field=models.OneToOneField(related_name='empresa_operador_caixa', null=True, blank=True,
                                       to=settings.AUTH_USER_MODEL),
        ),
    ]
