# -*- coding: utf-8 -*-
import os

from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'migra'

    def handle(self, *args, **options):
        os.system(
            "/usr/local/Cellar/python/2.7.9/bin/python /Applications/PyCharm.app/Contents/helpers/pycharm/django_manage.py makemigrations /Users/brenouchoa/PycharmProjects/erp")
        os.system(
            "/usr/local/Cellar/python/2.7.9/bin/python /Applications/PyCharm.app/Contents/helpers/pycharm/django_manage.py migrate /Users/brenouchoa/PycharmProjects/erp")