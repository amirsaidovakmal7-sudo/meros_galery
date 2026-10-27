"""Готовит фото товара в едином формате сразу при загрузке в админке,
чтобы первый посетитель страницы не ждал обработки."""
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from app import product_photos
from app.models import ProductImage


@receiver(post_save, sender=ProductImage)
def build_card_photo(sender, instance, **kwargs):
    if instance.image:
        product_photos.card_url(instance.image)


@receiver(post_delete, sender=ProductImage)
def remove_card_photo(sender, instance, **kwargs):
    if instance.image:
        product_photos.remove(instance.image)
