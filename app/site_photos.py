"""Фото на страницах сайта, которые заказчик меняет в админке.

Каждое место на странице — запись в SLOTS: ключ, страница, название для
админки, картинка по умолчанию и подсказка о формате. Строки в базе
(модель SitePhoto) создаются сами при открытии раздела в админке, поэтому
чтобы добавить новое место, достаточно дописать его сюда и в шаблон:

    <img src="{{ photos.<ключ> }}">

Если фото не загружено, на сайте остаётся картинка по умолчанию.
"""
import logging
import os
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

HOME = 'home'
ABOUT = 'about'
PAGES = [(HOME, 'Главная'), (ABOUT, 'О нас')]

WIDE = 'Горизонтальное, широкое (примерно 16:9). Края по бокам могут обрезаться.'
HERO = 'Горизонтальное, на весь экран. Главный объект лучше держать ближе к центру.'
VERTICAL = 'Вертикальное (примерно 4:5).'

# (ключ, страница, название в админке, картинка по умолчанию, подсказка)
SLOTS = [
    ('home_hero', HOME, 'Главная — заглавный экран (фото под видео)', 'filosophy.jpg',
     HERO + ' Видно, пока грузится видео, и если браузер не запустил видео.'),
    ('home_about', HOME, 'Главная — портрет в блоке «О нас»', 'dinara-crop.jpg',
     'Квадратное (1:1).'),
    ('home_events', HOME, 'Главная — баннер Events & Masterclasses', 'comunity.webp',
     'Горизонтальное, очень широкое (примерно 16:7). На телефоне показывается вертикально, по центру.'),
    ('home_instagram_1', HOME, 'Главная — Instagram, фото 1', 'about-hero.jpg', VERTICAL),
    ('home_instagram_2', HOME, 'Главная — Instagram, фото 2', 'comunity.webp', VERTICAL),
    ('home_instagram_3', HOME, 'Главная — Instagram, фото 3', 'direction.webp', VERTICAL),
    ('home_instagram_4', HOME, 'Главная — Instagram, фото 4', 'quote.jpg', VERTICAL),
    ('home_instagram_5', HOME, 'Главная — Instagram, фото 5', 'comunity.jpg', VERTICAL),

    ('about_hero', ABOUT, 'О нас — заглавный экран', 'about-hero.jpg', HERO),
    ('about_history', ABOUT, 'О нас — Наша история', 'ourhistory.jpg', WIDE),
    ('about_concept', ABOUT, 'О нас — Наша концепция', 'comunity.webp', WIDE),
    ('about_philosophy', ABOUT, 'О нас — Наша философия', 'filosophy.jpg', WIDE),
    ('about_vision', ABOUT, 'О нас — Слова основательницы (цитата)', 'quote.jpg',
     WIDE + ' На телефоне показывается вертикально, по центру.'),
    ('about_space_courtyard', ABOUT, 'О нас — Пространство: Courtyard', 'comunity.jpg',
     'Горизонтальное, панорамное (примерно 21:9). На телефоне — вертикально, по центру.'),
    ('about_space_retail', ABOUT, 'О нас — Пространство: Retail', 'quote.jpg',
     'Горизонтальное, панорамное (примерно 21:9). На телефоне — вертикально, по центру.'),
    ('about_space_workshop', ABOUT, 'О нас — Пространство: Workshop', 'direction.webp',
     'Горизонтальное, панорамное (примерно 21:9). На телефоне — вертикально, по центру.'),
    ('about_space_lounge', ABOUT, 'О нас — Пространство: Lounge', 'about-hero.jpg',
     'Горизонтальное, панорамное (примерно 21:9). На телефоне — вертикально, по центру.'),
    ('about_space_second_hand', ABOUT, 'О нас — Пространство: Second Hand', 'ourhistory.jpg',
     'Горизонтальное, панорамное (примерно 21:9). На телефоне — вертикально, по центру.'),
    ('about_space_reception', ABOUT, 'О нас — Пространство: Reception', 'comunity.webp',
     'Горизонтальное, панорамное (примерно 21:9). На телефоне — вертикально, по центру.'),
    ('about_directions', ABOUT, 'О нас — Четыре направления одной идеи', 'direction.webp', WIDE),
    ('about_community', ABOUT, 'О нас — Сообщество', 'comunity.jpg', WIDE),
]

SLOT_BY_KEY = {slot[0]: slot for slot in SLOTS}
KEYS = list(SLOT_BY_KEY)

# Загруженное фото уменьшается до этого размера по длинной стороне:
# хватает на весь экран retina-ноутбука, а файл с телефона на 10-20 МБ
# не тормозит сайт.
MAX_SIDE = 2560
JPEG_QUALITY = 85


def default_url(key):
    return '/static/media/' + SLOT_BY_KEY[key][3]


def ensure_slots():
    """Создаёт в базе недостающие места и обновляет их названия и порядок."""
    from app.models import SitePhoto

    existing = {p.key: p for p in SitePhoto.objects.all()}
    for order, (key, page, title, _default, _hint) in enumerate(SLOTS):
        photo = existing.get(key)
        if photo is None:
            SitePhoto.objects.create(key=key, page=page, title=title, my_order=order)
        elif (photo.page, photo.title, photo.my_order) != (page, title, order):
            photo.page, photo.title, photo.my_order = page, title, order
            photo.save(update_fields=['page', 'title', 'my_order'])


def urls(page=None):
    """{ключ: URL} для шаблона — один запрос к базе.
    Если фото не загружено, подставляется картинка по умолчанию."""
    from app.models import SitePhoto

    result = {key: default_url(key) for key in KEYS
              if page is None or SLOT_BY_KEY[key][1] == page}
    uploaded = SitePhoto.objects.filter(key__in=list(result)).exclude(image='')
    for photo in uploaded:
        result[photo.key] = photo.image.url
    return result


def shrink(image_field):
    """Уменьшает только что загруженное фото до MAX_SIDE и сохраняет как JPEG.

    Возвращает ContentFile для записи в поле или None, если фото и так
    небольшое или его не удалось прочитать (тогда остаётся оригинал)."""
    try:
        image_field.open('rb')
        with Image.open(image_field) as src:
            src.load()
            im = ImageOps.exif_transpose(src)
            if max(im.size) <= MAX_SIDE and getattr(image_field, 'size', 0) <= 1.5 * 1024 * 1024:
                return None
            if im.mode in ('RGBA', 'LA', 'P'):
                im = im.convert('RGBA')
                canvas = Image.new('RGB', im.size, (255, 255, 255))
                canvas.paste(im, mask=im.getchannel('A'))
                im = canvas
            else:
                im = im.convert('RGB')
            im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
            buf = BytesIO()
            im.save(buf, 'JPEG', quality=JPEG_QUALITY, optimize=True, progressive=True)
    except Exception:
        logger.exception('Не удалось уменьшить фото %s', image_field.name)
        return None
    stem = os.path.splitext(os.path.basename(image_field.name))[0][:80] or 'photo'
    return ContentFile(buf.getvalue(), name=stem + '.jpg')
