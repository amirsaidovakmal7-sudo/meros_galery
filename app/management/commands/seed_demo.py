"""Демо-данные, чтобы показать заказчику, как выглядят полные сетки.

    python manage.py seed_demo          # добавить демо-товары, новости и отзывы
    python manage.py seed_demo --clear  # удалить всё, что создала эта команда

Все демо-записи помечены префиксом «[ДЕМО]», реальные данные не затрагиваются.
Фотографии берутся из app/static/media (реальные фото галереи) и копируются
в MEDIA_ROOT/media/. Перед запуском на сайте заказчика — заменить или удалить.
"""
import datetime
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from app.models import Feedbacks, News, ProductCategory, Products

PREFIX = '[ДЕМО]'
PHOTOS = ['quote.jpg', 'comunity.webp', 'direction.webp', 'about-hero.jpg',
          'comunity.jpg', 'filosophy.jpg', 'ourhistory.jpg']
PRODUCTS_PER_CATEGORY = 12


class Command(BaseCommand):
    help = 'Создать (или удалить с --clear) демо-товары, новости и отзывы.'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Удалить демо-записи')

    def handle(self, *args, **options):
        if options['clear']:
            Products.objects.filter(name__startswith=PREFIX).delete()
            News.objects.filter(title__startswith=PREFIX).delete()
            Feedbacks.objects.filter(text__startswith=PREFIX).delete()
            self.stdout.write('Демо-записи удалены.')
            return

        photos = self.copy_photos()

        for category in ProductCategory.objects.all():
            existing = Products.objects.filter(product_category=category).count()
            for i in range(max(PRODUCTS_PER_CATEGORY - existing, 0)):
                Products.objects.create(
                    name=f'{PREFIX} {category.category_name} {i + 1}',
                    photo1=photos[(i + category.pk) % len(photos)],
                    price=str(90000 + 35000 * i),
                    allowed_amount=1,
                    desc='Демонстрационное описание товара. Заменяется настоящим.',
                    details='', carry='', status='Единственный экземпляр',
                    product_category=category,
                )

        news_count = News.objects.count()
        for i in range(max(6 - news_count, 0)):
            News.objects.create(
                photo=photos[i % len(photos)],
                title=f'{PREFIX} Новость {i + 1}',
                date=datetime.date.today() - datetime.timedelta(days=7 * i),
                description='Демонстрационный текст новости, чтобы оценить сетку карточек.',
            )

        for i, (name, role) in enumerate([('Имя Фамилия', 'Дизайнер интерьеров'),
                                          ('Имя Фамилия', 'Коллекционер'),
                                          ('Имя Фамилия', 'Гость галереи')]):
            Feedbacks.objects.create(
                text=f'{PREFIX} Демонстрационный отзыв: пространство, в котором хочется остаться.',
                author_name=name, author_role=role,
            )
        self.stdout.write('Демо-данные созданы.')

    def copy_photos(self):
        source = Path(settings.BASE_DIR) / 'app' / 'static' / 'media'
        target = Path(settings.MEDIA_ROOT) / 'media'
        target.mkdir(parents=True, exist_ok=True)
        names = []
        for photo in PHOTOS:
            shutil.copyfile(source / photo, target / f'demo_{photo}')
            names.append(f'media/demo_{photo}')
        return names
