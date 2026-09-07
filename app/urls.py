from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page),
    path('about', views.about_page),
    path('events', views.events_page),
    path('shop', views.shop_page),
    path('news', views.news),
    path('news/<int:pk>', views.exact_new),
    path('shop/product/<int:pk>', views.product_page),
    path('events/<int:pk>', views.event_page),
    path('events/masterclass/<int:pk>', views.masterclass_page),
    path('shop/category/<int:pk>', views.category_product),
    path('add_to_cart_product/<int:pk>', views.add_to_cart_product),
    path('cart', views.cart_page),
    path('add_to_cart_event/<int:pk>', views.add_to_cart_event),
    path('add_to_cart_masterclass/<int:pk>', views.add_to_cart_masterclass),
    path('remove_from_cart_product/<int:pk>', views.remove_from_cart_product),
    path('remove_from_cart_event/<int:pk>', views.remove_from_cart_event),
    path('remove_from_cart_masterclass/<int:pk>', views.remove_from_cart_masterclass),



]

