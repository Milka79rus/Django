import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from phones.models import Phone


class Command(BaseCommand):
    help = 'Выгрузка каталога телефонов из CSV и сохранение в базу данных'

    def handle(self, *args, **options):
        with open('phones.csv', 'r', encoding='utf-8') as file:
            phones = list(csv.DictReader(file, delimiter=';'))

        for phone in phones:
            release_date = datetime.strptime(phone['release_date'], '%Y-%m-%d').date()
            slug_value = slugify(phone['name'])

            Phone.objects.update_or_create(
                id=int(phone['id']),
                defaults={
                    'name': phone['name'],
                    'price': float(phone['price']),
                    'image': phone['image'],
                    'release_date': release_date,
                    'lte_exists': phone['lte_exists'].lower() == 'true',
                    'slug': slug_value,
                },
            )

        self.stdout.write(self.style.SUCCESS(f'Импортировано {len(phones)} телефонов'))
