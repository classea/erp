# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Lista dos modelos para registrar no Admin'

    def handle(self, *args, **options):
        contents = open('./modelos', 'w')
        for c in ContentType.objects.filter(app_label='classea').all():
            cl = c.model_class()
            contents.write(
                "{0}.Admin.form = modelform_factory({0}, fields=('__all__'), exclude=(), localized_fields=('__all__'))\n".format(
                    cl.__name__))
            contents.write("admin.site.register({0}, {0}.Admin)\n".format(cl.__name__))
        contents.close()
