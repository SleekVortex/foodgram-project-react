from django.core.management import BaseCommand
from recipes.models import Tag

FILE_PATH = './data/ingredients.csv'


class Command(BaseCommand):
    help = 'Создаются теги.'

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
        self._create_tags()
        self.stdout.write(
            self.style.SUCCESS('Данные успешно загружены и тэги созданы.'))
