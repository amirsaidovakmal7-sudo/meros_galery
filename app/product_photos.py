"""Единый формат фото товаров для карточек и галереи.

Студийные фото приходят разного формата (3:4, 4:3, 1:1), а предмет занимает
от 40% до 100% кадра. Поэтому карточки получались неровными: одни предметы
обрезались по краям, другие тонули в белом поле.

Здесь белый фон обрезается вплотную к предмету, вокруг остаётся тонкое
одинаковое поле, и копия сохраняется лёгким WebP в MEDIA_ROOT/cards/.
Отступ внутри карточки задаёт CSS (класс .product-photo), поэтому любой
предмет вписывается в карточку целиком и максимально крупно.

Оригиналы не меняются. Если у фото не белый фон (интерьерный снимок),
оно не обрезается, а только уменьшается.
"""
import hashlib
import logging
import os
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image, ImageChops, ImageFilter, ImageOps

logger = logging.getLogger(__name__)

# При изменении алгоритма поднять версию: копии пересоздадутся под новыми именами.
VERSION = 1
OUT_DIR = 'cards'
MAX_SIDE = 1400        # px по длинной стороне: хватает и для галереи на retina
MARGIN = 0.025         # поле вокруг предмета, доля от его длинной стороны
BG_MIN = 232           # фон светлее этого считается студийным
BG_TOLERANCE = 10      # насколько пиксель может отличаться от фона и остаться фоном
WEBP_QUALITY = 86


def card_name(name):
    stem = os.path.splitext(os.path.basename(name))[0][:80]
    digest = hashlib.md5(f'{name}|{VERSION}'.encode()).hexdigest()[:8]
    return f'{OUT_DIR}/{stem}-{digest}.webp'


def _flatten(im):
    im = ImageOps.exif_transpose(im)
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
        im = im.convert('RGBA')
        canvas = Image.new('RGB', im.size, (255, 255, 255))
        canvas.paste(im, mask=im.getchannel('A'))
        return canvas
    return im.convert('RGB')


def _studio_background(im):
    """Цвет фона, если все четыре угла одинаково светлые, иначе None."""
    w, h = im.size
    patch = max(4, min(w, h) // 60)
    boxes = [(0, 0), (w - patch, 0), (0, h - patch), (w - patch, h - patch)]
    colors = [im.crop((x, y, x + patch, y + patch)).resize((1, 1), Image.BOX).getpixel((0, 0))
              for x, y in boxes]
    if any(min(c) < BG_MIN for c in colors):
        return None
    spread = max(max(c[i] for c in colors) - min(c[i] for c in colors) for i in range(3))
    if spread > BG_TOLERANCE:
        return None
    return tuple(sorted(c[i] for c in colors)[2] for i in range(3))


def _distance(im, bg):
    """Насколько каждый пиксель отличается от фона (максимум по каналам)."""
    r, g, b = ImageChops.difference(im, Image.new('RGB', im.size, bg)).split()
    return ImageChops.lighter(ImageChops.lighter(r, g), b)


def _object_box(distance):
    mask = distance.point(lambda v: 255 if v > BG_TOLERANCE else 0)
    # Убираем пылинки и шум сжатия, чтобы они не растягивали рамку.
    mask = mask.filter(ImageFilter.MedianFilter(5))
    return mask.getbbox()


def _whiten(im, distance):
    """Доводит студийный фон до чистого белого, как у карточки.

    Без этого фон фото (обычно 250-254 с лёгким градиентом) и белое поле
    вокруг расходятся, и на экране проступает прямоугольник обрезки.
    Переход плавный, поэтому мягкие тени и края стекла остаются."""
    lo, hi = BG_TOLERANCE // 2, BG_TOLERANCE * 2
    alpha = distance.point(lambda v: 0 if v <= lo else 255 if v >= hi else (v - lo) * 255 // (hi - lo))
    white = Image.new('RGB', im.size, (255, 255, 255))
    return Image.composite(im, white, alpha)


def normalize(im):
    """Обрезает студийный фон вокруг предмета и уменьшает до MAX_SIDE."""
    im = _flatten(im)
    bg = _studio_background(im)
    distance = _distance(im, bg) if bg else None
    box = _object_box(distance) if bg else None
    if box:
        im = _whiten(im, distance)
        left, top, right, bottom = box
        pad = round(max(right - left, bottom - top) * MARGIN)
        w, h = right - left + 2 * pad, bottom - top + 2 * pad
        # Если предмет касается края кадра, поле дорисовывается белым.
        canvas = Image.new('RGB', (w, h), (255, 255, 255))
        crop = (max(left - pad, 0), max(top - pad, 0),
                min(right + pad, im.width), min(bottom + pad, im.height))
        canvas.paste(im.crop(crop), (crop[0] - (left - pad), crop[1] - (top - pad)))
        im = canvas
    im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    return im


def build(image_field, name=None):
    """Создаёт нормализованную копию и возвращает её имя в хранилище."""
    name = name or card_name(image_field.name)
    image_field.open('rb')
    try:
        with Image.open(image_field) as src:
            im = normalize(src)
    finally:
        image_field.close()
    buf = BytesIO()
    im.save(buf, 'WEBP', quality=WEBP_QUALITY, method=6)
    if default_storage.exists(name):
        default_storage.delete(name)
    saved = default_storage.save(name, ContentFile(buf.getvalue()))
    if saved != name:  # параллельный запрос успел первым
        default_storage.delete(saved)
    return name


def card_url(image_field):
    """URL нормализованной копии. Создаёт её при первом обращении,
    при любой ошибке отдаёт оригинал, чтобы страница не ломалась."""
    if not image_field:
        return ''
    name = card_name(image_field.name)
    try:
        if not default_storage.exists(name):
            if not image_field.storage.exists(image_field.name):
                return image_field.url  # оригинала нет на диске, обрабатывать нечего
            build(image_field, name)
        return default_storage.url(name)
    except Exception:
        logger.exception('Не удалось подготовить фото товара %s', image_field.name)
        return image_field.url


def remove(image_field):
    name = card_name(image_field.name)
    if default_storage.exists(name):
        default_storage.delete(name)
