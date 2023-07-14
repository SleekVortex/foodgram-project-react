import csv

from django.core.management import BaseCommand
from recipes.models import Ingredient

FILE_PATH = './data/ingredients.csv'


class Command(BaseCommand):
    help = 'Загружаются данные из csv - файла.'

    @staticmethod
    def _load_ingredients_data():
        with open(FILE_PATH, 'r', encoding='utf-8') as csv_file:
            file_reader = csv.reader(csv_file)
            for row in file_reader:
                Ingredient.objects.get_or_create(
                    name=row[0], measurement_unit=row[1]
                )

    def handle(self, *args, **options):
        self._load_ingredients_data()
        self.stdout.write(self.style.SUCCESS('Данные успешно загружены!'))
