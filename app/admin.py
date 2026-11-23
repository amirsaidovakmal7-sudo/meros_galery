from django.contrib import admin
from django.utils.html import format_html
from .models import *
from . import site_photos
from adminsortable2.admin import SortableAdminMixin


class PhotoProductInline(admin.StackedInline):
    model = ProductImage
    extra = 1

class PhotoNewInline(admin.StackedInline):
    model = NewsImage
    extra = 1

class PhotoMasterclassInline(admin.StackedInline):
    model = MasterclassImage
    extra = 1


class PhotoEventInline(admin.StackedInline):
    model = EventsImage
    extra = 1

class PhotoWorkerInline(admin.StackedInline):
    model = WorkersImage
    extra = 1

class ProductPeriodInline(admin.TabularInline):
    model = ProductPeriodField
    extra = 1

class ProductMaterialInline(admin.TabularInline):
    model = ProductMaterialField
    extra = 1

class ProductSizeInline(admin.TabularInline):
    model = ProductSizeField
    extra = 1

class ProductConditionInline(admin.TabularInline):
    model = ProductConditionField
    extra = 1

class ProductStatusInline(admin.TabularInline):
    model = ProductStatusField
    extra = 1

class ArtProductAuthorInline(admin.TabularInline):
    model = ArtProductAuthorField
    extra = 1

class ArtProductYearInline(admin.TabularInline):
    model = ArtProductYearField
    extra = 1

class ArtProductTechniqueInline(admin.TabularInline):
    model = ArtProductTechniqueField
    extra = 1

@admin.register(News)
class NewsAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [PhotoNewInline]


@admin.register(NewsImage)
class NewsImageAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['id', 'new']

@admin.register(Masterclasses)
class MasterclassesAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [PhotoMasterclassInline]

@admin.register(MasterclassImage)
class MasterclassImageAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['id', 'masterclass']



@admin.register(ProductCategory)
class ProductCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass



@admin.register(ProductImage)
class ProductImageAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['my_order', 'product']


@admin.register(Products)
class ProductsRetailAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'product_category', 'my_order']
    inlines = [PhotoProductInline, ProductPeriodInline, ProductMaterialInline, ProductSizeInline, ProductConditionInline,
               ProductStatusInline, ArtProductAuthorInline, ArtProductYearInline, ArtProductTechniqueInline]



@admin.register(Feedbacks)
class FeedbacksAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass

@admin.register(Events)
class EventsAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [PhotoEventInline]


@admin.register(EventsImage)
class EventsImageAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['id', 'event']


@admin.register(Workers)
class WorkersAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [PhotoWorkerInline]


@admin.register(WorkersImage)
class WorkersImageAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


@admin.register(SitePhoto)
class SitePhotoAdmin(admin.ModelAdmin):
    """Набор мест фиксирован (app/site_photos.py): заказчик только меняет фото."""
    list_display = ['preview_small', 'title', 'page_name', 'is_custom']
    list_display_links = ['preview_small', 'title']
    list_filter = ['page']
    fields = ['title', 'hint', 'preview', 'image']
    readonly_fields = ['title', 'hint', 'preview']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(key__in=site_photos.KEYS)

    def changelist_view(self, request, extra_context=None):
        site_photos.ensure_slots()
        return super().changelist_view(request, extra_context)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def _current_url(self, obj):
        return obj.image.url if obj.image else site_photos.default_url(obj.key)

    @admin.display(description='Фото')
    def preview_small(self, obj):
        return format_html(
            '<img src="{}" style="width:120px;height:68px;object-fit:cover;border-radius:4px;display:block">',
            self._current_url(obj))

    @admin.display(description='Сейчас на сайте')
    def preview(self, obj):
        label = 'Загруженное фото' if obj.image else 'Стандартное фото сайта'
        return format_html(
            '<img src="{}" style="max-width:480px;max-height:320px;border-radius:4px;display:block">'
            '<div style="margin-top:6px;color:#666">{}</div>',
            self._current_url(obj), label)

    @admin.display(description='Какое фото подойдёт')
    def hint(self, obj):
        return site_photos.SLOT_BY_KEY[obj.key][4]

    @admin.display(description='Страница', ordering='page')
    def page_name(self, obj):
        return obj.get_page_display()

    @admin.display(description='Своё фото', boolean=True)
    def is_custom(self, obj):
        return bool(obj.image)




