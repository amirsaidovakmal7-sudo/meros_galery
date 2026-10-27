"""Готовит фото товаров в едином формате для карточек (см. app/product_photos.py).

    python manage.py build_product_photos          # создать недостающие
    python manage.py build_product_photos --force  # пересоздать все

Новые фото обрабатываются сами при загрузке. Команда нужна один раз после
выкладки и после изменения алгоритма.
"""
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from app import product_photos
from app.models import ProductImage


class Command(BaseCommand):
    help = 'Создать фото товаров в едином формате для карточек.'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Пересоздать уже готовые')

    def handle(self, *args, force=False, **options):
        built = skipped = failed = 0
        for photo in ProductImage.objects.exclude(image=''):
            name = product_photos.card_name(photo.image.name)
            if not force and default_storage.exists(name):
                skipped += 1
                continue
            try:
                product_photos.build(photo.image, name)
                built += 1
            except Exception as exc:
                failed += 1
                self.stderr.write(f'{photo.image.name}: {exc}')
        self.stdout.write(self.style.SUCCESS(
            f'Готово: создано {built}, уже было {skipped}, ошибок {failed}.'))
