# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


# noinspection PySetFunctionToLiteral
class Migration(migrations.Migration):
    dependencies = [
        ('principal', '0005_auto_20150415_2007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='empresaativa',
            name='usuario',
            field=models.OneToOneField(related_name='usuario_empresa_ativa', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='lancamento',
            name='valor',
            field=models.DecimalField(verbose_name='Valor', max_digits=18, decimal_places=2),
        ),
        migrations.AlterUniqueTogether(
            name='conta',
            unique_together=set([('empresa', 'conta'), ('empresa', 'abr')]),
        ),
    ]
