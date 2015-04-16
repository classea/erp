# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('principal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmpresaAtiva',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data Cria\xe7\xe3o')),
                ('data_alteracao', models.DateTimeField(auto_now=True, verbose_name='Data Altera\xe7\xe3o')),
                ('empresa', models.ForeignKey(blank=True, to='principal.Empresa', null=True)),
                ('usuario', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['usuario'],
                'verbose_name': 'Empresa',
                'verbose_name_plural': 'Empresa Ativa',
            },
        ),
    ]
