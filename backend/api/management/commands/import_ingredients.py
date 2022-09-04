import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import data from csv-file.'

    def handle(self, *args, **options):
        answer = input(
            'Do you want to clean up the Ingredients database? [Y/N]: '
        ).lower()
        if answer == 'y':
            Ingredient.objects.all().delete()
        elif answer == 'n':
            return 'The operation is skipped.'
        else:
            return 'Invalid value.'
        with open(
            os.path.join(settings.STATIC_ROOT, 'backend.data', 'ingredients.csv'),
            'r', encoding='utf-8'
            ) as csv_file:
            reader = csv.DictReader(csv_file)
            Ingredient.objects.bulk_create(
                Ingredient(**data) for data in reader
            )
            self.stdout.write(
                'Выполнен импорт данных для таблицы Ingredient.'
            )
        return 'Выполнен импорт данных для таблицы Ingredient.'
