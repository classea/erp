# -*- coding: utf-8 -*-
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand
from django.utils.functional import Promise


class Command(BaseCommand):
    help = 'Arrumar nomes permissoes'

    def handle(self, *args, **options):
        perms = Permission.objects.all()
        for p in perms:
            p.name = u"{} {}".format(p.content_type.model, p.codename)[:50]
            p.save()

        for c in ContentType.objects.all():
            cl = c.model_class()
            # Promises classes are from translated, mostly django-internal models. ignore them.
            if cl and not isinstance(cl._meta.verbose_name, Promise):
                new_name = cl._meta.verbose_name
                if c.name != new_name:
                    # print u"Updating ContentType's name: '%s' -> '%s'" % (c.name, new_name)
                    c.name = new_name
                    c.save()