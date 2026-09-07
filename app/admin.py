from django.contrib import admin
from .models import *
from adminsortable2.admin import SortableAdminMixin, SortableStackedInline


@admin.register(News)
class NewsAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass

@admin.register(Masterclasses)
class MasterclassesAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


@admin.register(ProductCategory)
class ProductCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass



class ProductInline(SortableStackedInline):
    model = Products



@admin.register(Products)
class ProductsRetailAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'product_category', 'my_order']
    inline = [ProductInline]



@admin.register(Feedbacks)
class FeedbacksAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass

@admin.register(Events)
class EventsAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Workers)
class WorkersAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass




