from django.test import SimpleTestCase
from PIL import Image, ImageDraw

from app import product_photos


def studio_shot(size, box, bg=(254, 254, 254), color=(120, 80, 40)):
    im = Image.new('RGB', size, bg)
    ImageDraw.Draw(im).rectangle(box, fill=color)
    return im


class NormalizeTests(SimpleTestCase):
    def test_trims_white_background_to_object(self):
        # Широкая чаша в середине горизонтального кадра, вокруг много фона.
        out = product_photos.normalize(studio_shot((1448, 1086), (300, 450, 1100, 650)))
        pad = round(801 * product_photos.MARGIN)
        self.assertEqual(out.size, (801 + 2 * pad, 201 + 2 * pad))

    def test_background_becomes_pure_white(self):
        out = product_photos.normalize(studio_shot((800, 800), (200, 200, 600, 600), bg=(250, 249, 251)))
        self.assertEqual(out.getpixel((1, 1)), (255, 255, 255))

    def test_object_touching_edge_gets_margin(self):
        # Носик чайника упирается в левый край исходного кадра.
        out = product_photos.normalize(studio_shot((1000, 1000), (0, 300, 600, 700)))
        self.assertEqual(out.getpixel((1, out.height // 2)), (255, 255, 255))

    def test_photo_without_studio_background_is_not_cropped(self):
        im = Image.new('RGB', (1600, 1200), (60, 90, 120))
        out = product_photos.normalize(im)
        self.assertEqual(out.size, (1400, 1050))

    def test_transparent_png_is_flattened_on_white(self):
        im = Image.new('RGBA', (600, 600), (0, 0, 0, 0))
        ImageDraw.Draw(im).ellipse((200, 200, 400, 400), fill=(30, 30, 30, 255))
        out = product_photos.normalize(im)
        self.assertEqual(out.mode, 'RGB')
        self.assertLess(out.width, 260)

    def test_card_name_changes_with_version(self):
        name = product_photos.card_name('media/чайник.png')
        self.assertTrue(name.startswith('cards/чайник-'))
        self.assertTrue(name.endswith('.webp'))
