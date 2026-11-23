import os
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


import shutil
import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from app import site_photos
from app.models import SitePhoto


def upload(size=(800, 600), name='photo.png', fmt='PNG'):
    buf = BytesIO()
    Image.new('RGB', size, (200, 120, 60)).save(buf, fmt)
    return SimpleUploadedFile(name, buf.getvalue())


class SitePhotoTests(TestCase):
    def setUp(self):
        self.media = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media, ignore_errors=True)

    def test_defaults_without_uploads(self):
        urls = site_photos.urls()
        self.assertEqual(set(urls), set(site_photos.KEYS))
        self.assertEqual(urls['about_history'], '/static/media/ourhistory.jpg')

    def test_urls_filtered_by_page(self):
        self.assertTrue(all(k.startswith('home_') for k in site_photos.urls(site_photos.HOME)))

    def test_ensure_slots_creates_every_place_once(self):
        site_photos.ensure_slots()
        site_photos.ensure_slots()
        self.assertEqual(SitePhoto.objects.count(), len(site_photos.SLOTS))

    def test_uploaded_photo_replaces_default(self):
        site_photos.ensure_slots()
        photo = SitePhoto.objects.get(key='home_events')
        photo.image = upload()
        photo.save()
        self.assertEqual(site_photos.urls()['home_events'], photo.image.url)

    def test_large_photo_is_shrunk(self):
        photo = SitePhoto.objects.create(key='about_hero', page='about', title='t')
        photo.image = upload((4000, 3000))
        photo.save()
        with Image.open(photo.image.path) as im:
            self.assertEqual(im.size, (site_photos.MAX_SIDE, 1920))

    def test_replacing_photo_deletes_old_file(self):
        photo = SitePhoto.objects.create(key='about_hero', page='about', title='t')
        photo.image = upload(name='first.png')
        photo.save()
        old_path = photo.image.path
        photo.image = upload(name='second.png')
        photo.save()
        self.assertFalse(os.path.exists(old_path))

    def test_pages_render_with_photos(self):
        site_photos.ensure_slots()
        photo = SitePhoto.objects.get(key='about_history')
        photo.image = upload()
        photo.save()
        about = self.client.get('/about').content.decode()
        self.assertIn(photo.image.url, about)
        self.assertNotIn('/static/media/ourhistory.jpg"', about.split('id="story"')[1].split('</section>')[0])
        home = self.client.get('/').content.decode()
        self.assertIn('/static/media/comunity.webp', home)

    def test_admin_lists_and_uploads(self):
        from django.contrib.auth.models import User
        self.client.force_login(User.objects.create_superuser('a', 'a@a.a', 'p'))
        listing = self.client.get('/admin/app/sitephoto/')
        self.assertEqual(listing.status_code, 200)
        self.assertContains(listing, 'О нас — Наша история')
        self.assertNotContains(listing, '/admin/app/sitephoto/add/')
        photo = SitePhoto.objects.get(key='home_events')
        url = f'/admin/app/sitephoto/{photo.pk}/change/'
        self.assertContains(self.client.get(url), 'Какое фото подойдёт')
        response = self.client.post(url, {'image': upload()})
        self.assertEqual(response.status_code, 302)
        photo.refresh_from_db()
        self.assertTrue(photo.image)
        self.client.post(url, {'image-clear': 'on'})
        photo.refresh_from_db()
        self.assertFalse(photo.image)
        self.assertEqual(site_photos.urls()['home_events'], '/static/media/comunity.webp')
