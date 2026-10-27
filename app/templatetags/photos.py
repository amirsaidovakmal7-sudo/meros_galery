from django import template

from app import product_photos

register = template.Library()


@register.filter
def card_url(image_field):
    """{{ p.image.first.image|card_url }} — фото товара в едином формате."""
    return product_photos.card_url(image_field)
