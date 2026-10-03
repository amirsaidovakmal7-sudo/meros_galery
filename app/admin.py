from django.contrib import admin
from .models import *
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




