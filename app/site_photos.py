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

# (ключ, страница, название в админке, картинка по умолчанию, подсказка)
SLOTS = [
    ('home_hero', HOME, 'Главная — заглавный экран (фото под видео)', 'filosophy.jpg',
     HERO + ' Видно, пока грузится видео, и если браузер не запустил видео.'),
    ('home_about', HOME, 'Главная — портрет в блоке «О нас»', 'dinara-crop.jpg',
     'Квадратное (1:1).'),
    ('home_events', HOME, 'Главная — баннер Events & Masterclasses', 'comunity.webp',
     'Горизонтальное, очень широкое (примерно 16:7). На телефоне показывается вертикально, по центру.'),

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

# Блок Instagram внизу главной: 5 постов (модель InstagramPost).
# Картинки по умолчанию — пока пост не загружен.
INSTAGRAM_DEFAULTS = ['about-hero.jpg', 'comunity.webp', 'direction.webp', 'quote.jpg', 'comunity.jpg']
INSTAGRAM_MAX_SIDE = 1080  # карточки маленькие, 1080 px хватает с запасом
IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
VIDEO_EXTENSIONS = {'mp4', 'mov', 'm4v', 'webm'}
VIDEO_MAX_BYTES = 50 * 1024 * 1024

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


def extension(name):
    return os.path.splitext(name)[1].lower().lstrip('.')


def is_video(name):
    return extension(name) in VIDEO_EXTENSIONS


def validate_media(file):
    from django.core.exceptions import ValidationError

    ext = extension(file.name)
    if ext not in IMAGE_EXTENSIONS | VIDEO_EXTENSIONS:
        raise ValidationError('Нужно фото (JPG, PNG, WebP) или видео (MP4, MOV, WebM).')
    if ext in VIDEO_EXTENSIONS and file.size > VIDEO_MAX_BYTES:
        raise ValidationError('Видео больше 50 МБ — сократите или сожмите его (лучше всего — короткий MP4).')


def ensure_instagram_posts():
    from app.models import InstagramPost

    existing = set(InstagramPost.objects.values_list('position', flat=True))
    for position in range(1, len(INSTAGRAM_DEFAULTS) + 1):
        if position not in existing:
            InstagramPost.objects.create(position=position)


def instagram_posts():
    """5 карточек для шаблона: url файла, видео или нет, ссылка на пост."""
    from app.models import InstagramPost

    saved = {p.position: p for p in InstagramPost.objects.all()}
    posts = []
    for position, default in enumerate(INSTAGRAM_DEFAULTS, 1):
        post = saved.get(position)
        if post and post.media:
            posts.append({'url': post.media.url, 'is_video': post.is_video, 'link': post.link})
        else:
            posts.append({'url': '/static/media/' + default, 'is_video': False,
                          'link': post.link if post else ''})
    return posts


def prepare_upload(instance, field, max_side=None):
    """Перед сохранением: уменьшает новое загруженное фото и возвращает
    имя старого файла, чтобы после сохранения удалить его."""
    old = None
    if instance.pk:
        old = type(instance).objects.filter(pk=instance.pk).values_list(field, flat=True).first()
    file = getattr(instance, field)
    if file and not getattr(file, '_committed', True) and not is_video(file.name):
        smaller = shrink(file, max_side or MAX_SIDE)
        if smaller is not None:
            file.save(smaller.name, smaller, save=False)
    return old


def delete_replaced(instance, field, old):
    """Старый файл больше нигде не используется — удаляем, чтобы не копился мусор."""
    file = getattr(instance, field)
    if old and old != file.name and file.storage.exists(old):
        file.storage.delete(old)


def shrink(image_field, max_side=MAX_SIDE):
    """Уменьшает только что загруженное фото до max_side и сохраняет как JPEG.

    Возвращает ContentFile для записи в поле или None, если фото и так
    небольшое или его не удалось прочитать (тогда остаётся оригинал)."""
    try:
        image_field.open('rb')
        with Image.open(image_field) as src:
            src.load()
            im = ImageOps.exif_transpose(src)
            if max(im.size) <= max_side and getattr(image_field, 'size', 0) <= 1.5 * 1024 * 1024:
                return None
            if im.mode in ('RGBA', 'LA', 'P'):
                im = im.convert('RGBA')
                canvas = Image.new('RGB', im.size, (255, 255, 255))
                canvas.paste(im, mask=im.getchannel('A'))
                im = canvas
            else:
                im = im.convert('RGB')
            im.thumbnail((max_side, max_side), Image.LANCZOS)
            buf = BytesIO()
            im.save(buf, 'JPEG', quality=JPEG_QUALITY, optimize=True, progressive=True)
    except Exception:
        logger.exception('Не удалось уменьшить фото %s', image_field.name)
        return None
    stem = os.path.splitext(os.path.basename(image_field.name))[0][:80] or 'photo'
    return ContentFile(buf.getvalue(), name=stem + '.jpg')
