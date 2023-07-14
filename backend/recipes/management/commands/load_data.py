import csv

from django.core.management import BaseCommand
from recipes.models import Ingredient, Tag

FILE_PATH = './data/ingredients.csv'


class Command(BaseCommand):
    help = 'Выполнются команды загрузки ингредиентов и создания тэгов'

    @staticmethod
    def _load_ingredients_data():
        with open(FILE_PATH, 'r', encoding='utf-8') as csv_file:
            file_reader = csv.reader(csv_file)
            for row in file_reader:
                name = row[0]
                measurement_unit = row[1]
                Ingredient.objects.get_or_create(
                    name=name, measurement_unit=measurement_unit
                )

    @staticmethod
    def _create_tags():
        data = [
            {'name': 'Горячее', 'color': '#FF0000', 'slug': 'hot'},
            {'name': 'Холодное', 'color': '#00FFFF', 'slug': 'cold'},
            {'name': 'Десерт', 'color': '#FFFF00', 'slug': 'dessert'},
        ]
        for tag_data in data:
            Tag.objects.create(**tag_data)

    def handle(self, *args, **options):
        self._load_ingredients_data()
        self._create_tags()
        self.stdout.write(
            self.style.SUCCESS('Данные успешно загружены и тэги созданы.'))
