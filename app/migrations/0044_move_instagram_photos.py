"""Создаёт 5 Instagram-постов и переносит в них фото, которые уже были
загружены в «Фото на страницах» (места home_instagram_1…5). Файлы на диске
не трогаются — посты просто ссылаются на те же файлы."""
from django.db import migrations

POSTS = 5


def forwards(apps, schema_editor):
    SitePhoto = apps.get_model('app', 'SitePhoto')
    InstagramPost = apps.get_model('app', 'InstagramPost')
    for position in range(1, POSTS + 1):
        old = SitePhoto.objects.filter(key=f'home_instagram_{position}').first()
        media = old.image.name if old and old.image else ''
        post, created = InstagramPost.objects.get_or_create(position=position, defaults={'media': media})
        if not created and not post.media and media:
            post.media = media
            post.save(update_fields=['media'])
    SitePhoto.objects.filter(key__startswith='home_instagram_').delete()


def backwards(apps, schema_editor):
    SitePhoto = apps.get_model('app', 'SitePhoto')
    InstagramPost = apps.get_model('app', 'InstagramPost')
    for post in InstagramPost.objects.all():
        if post.media and not post.media.name.lower().endswith(('.mp4', '.mov', '.m4v', '.webm')):
            SitePhoto.objects.update_or_create(
                key=f'home_instagram_{post.position}',
                defaults={'page': 'home', 'title': f'Главная — Instagram, фото {post.position}',
                          'image': post.media.name, 'my_order': 2 + post.position},
            )


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0043_instagrampost'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
