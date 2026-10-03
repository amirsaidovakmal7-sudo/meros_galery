from django.db import models





class News(models.Model):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    title_en = models.CharField(max_length=256, verbose_name='Заголовок на англ')
    title_uz = models.CharField(max_length=256, verbose_name='Заголовок на узб')
    date = models.DateField('Дата')
    description = models.TextField('Описание')
    description_en = models.TextField('Описание на англ')
    description_uz = models.TextField('Описание на узб')
    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['my_order']

    def __str__(self):
        return self.title


class NewsImage(models.Model):
    new = models.ForeignKey(News, on_delete=models.CASCADE, related_name="image")

    image = models.ImageField(upload_to='media', verbose_name='Фото новости')

    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = "Фото новости"
        verbose_name_plural = "Фотки новости"
        ordering = ['my_order']


class Masterclasses(models.Model):
    name = models.CharField(max_length=128, verbose_name='Название мастеркласса')
    name_en = models.CharField(max_length=128, verbose_name='Название мастеркласса на англ')
    name_uz = models.CharField(max_length=128, verbose_name='Название мастеркласса на узб ')
    tamada = models.CharField(max_length=128, verbose_name='Ведущий')
    tamada_en = models.CharField(max_length=128, verbose_name='Ведущий на англ')
    tamada_uz = models.CharField(max_length=128, verbose_name='Ведущий на узб')
    date = models.DateField('Дата мастеркалсса')
    time = models.TimeField('Время мастеркласса')
    desc = models.TextField('Описание')
    desc_en = models.TextField('Описание на англ')
    desc_uz = models.TextField('Описание на узб')
    price = models.IntegerField('Цена', default=0)
    price_usd = models.TextField('Цена (в долларах)', default='')
    price_eur = models.TextField('Цена (в евро)', default='')
    allowed_amount = models.IntegerField(default=0, verbose_name='Доступно мест')
    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )
    class Meta:
        verbose_name = 'Мастеркласс'
        verbose_name_plural = 'Мастерклассы'
        ordering = ['my_order']

    def __str__(self):
        return self.name


class MasterclassImage(models.Model):
    masterclass = models.ForeignKey(Masterclasses, on_delete=models.CASCADE, related_name="image")

    image = models.ImageField(upload_to='media', verbose_name='Фото мастеркласса')

    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = "Фото мастеркласса"
        verbose_name_plural = "Фотки мастеркласса"
        ordering = ['my_order']






class Feedbacks(models.Model):
    text = models.TextField('Текст отзыва')
    text_en = models.TextField('Текст отзыва на англ')
    text_uz = models.TextField('Текст отзыва на узб')
    author_name = models.CharField('Имя автора отзыва', max_length=128, blank=True)
    author_role = models.CharField('Род деятельности автора', max_length=128, blank=True)
    author_name_en = models.CharField('Имя автора отзыва на англ', max_length=128, blank=True)
    author_role_en = models.CharField('Род деятельности автора на англ', max_length=128, blank=True)
    author_name_uz = models.CharField('Имя автора отзыва на узб', max_length=128, blank=True)
    author_role_uz = models.CharField('Род деятельности автора на узб', max_length=128, blank=True)
    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['my_order']

    def __str__(self):
        return self.text



class Events(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название ивента')
    name_en = models.CharField(max_length=256, verbose_name='Название ивента на англ')
    name_uz = models.CharField(max_length=256, verbose_name='Название ивента на узб')
    desc = models.TextField('Описание')
    desc_en = models.TextField('Описание на англ')
    desc_uz = models.TextField('Описание на узб')
    allowed_amount = models.IntegerField(default=0, verbose_name='Доступно мест')
    place_abilities = models.TextField('Возмонжости пространства')
    place_abilities_en = models.TextField('Возмонжости пространства на англ')
    place_abilities_uz = models.TextField('Возмонжости пространства на узб')
    extra_service = models.TextField(null=True, verbose_name='Доп услуги')
    extra_service_en = models.TextField(null=True, verbose_name='Доп услуги на англ')
    extra_service_uz = models.TextField(null=True, verbose_name='Доп услуги на англ')
    price = models.TextField(verbose_name='Цена за место', default='')
    price_usd = models.TextField('Цена (в долларах)', default='')
    price_eur = models.TextField('Цена (в евро)', default='')
    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Ивент'
        verbose_name_plural = 'Ивенты'
        ordering = ['my_order']

    def __str__(self):
        return self.name


class EventsImage(models.Model):
    event = models.ForeignKey(Events, on_delete=models.CASCADE, related_name="image")

    image = models.ImageField(upload_to='media', verbose_name='Фото ивента')

    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = "Фото ивента"
        verbose_name_plural = "Фотки ивента"
        ordering = ['my_order']


class ProductCategory(models.Model):
    category_name = models.CharField(max_length=128, verbose_name='Название категории')
    category_name_en = models.CharField(max_length=128, verbose_name='Название категории на англ')
    category_name_uz = models.CharField(max_length=128, verbose_name='Название категории на узб')
    cover_photo = models.ImageField(
        upload_to='media',
        blank=True,
        null=True,
        verbose_name='Фото-баннер категории',
        help_text='Если не загружено — на сайте показывается фото галереи по умолчанию',
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='Текст категории',
        help_text='Короткое описание категории. Показывается под названием категории на её странице и на главной.',
    )
    description_eng = models.TextField(
        blank=True,
        default='',
        verbose_name='Текст категории (на англ)',
        help_text='Короткое описание категории. Показывается под названием категории на её странице и на главной. (на англ)',
    )
    description_uz = models.TextField(
        blank=True,
        default='',
        verbose_name='Текст категории (на узб)',
        help_text='Короткое описание категории. Показывается под названием категории на её странице и на главной. (на узб)',
    )
    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['my_order']

    DEFAULT_COVERS = {
        'retail': '/static/media/quote.jpg',
        'vintage': '/static/media/about-hero.jpg',
        'secondhand': '/static/media/comunity.jpg',
        'art': '/static/media/direction.webp',
    }

    @property
    def cover_url(self):
        if self.cover_photo:
            return self.cover_photo.url
        key = self.category_name.replace(' ', '').lower()
        return self.DEFAULT_COVERS.get(key, '/static/media/comunity.webp')

    def __str__(self):
        return self.category_name


class Products(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название (Retail Product)')
    name_en = models.CharField(max_length=256, verbose_name='Название (Retail Product) на англ')
    name_uz = models.CharField(max_length=256, verbose_name='Название (Retail Product) на узб')
    price = models.CharField(max_length=128, verbose_name='Цена')
    price_usd = models.TextField('Цена (в долларах)', default='')
    price_eur = models.TextField('Цена (в евро)', default='')
    allowed_amount = models.IntegerField(default=0, verbose_name='Доступно продуктов')
    desc = models.TextField('Описание продукта')
    desc_en = models.TextField('Описание продуктана англ')
    desc_uz = models.TextField('Описание продукта на узб ')
    details = models.TextField('Особенности кроя и отделки')
    details_en = models.TextField('Особенности кроя и отделки на англ ')
    details_uz = models.TextField('Особенности кроя и отделки на узб')
    carry = models.TextField('Рекомендации по уходу')
    carry_en = models.TextField('Рекомендации по уходу на англ')
    carry_uz = models.TextField('Рекомендации по уходу на узб')
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, default='')

    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['my_order']

    def __str__(self):
        return self.name


class ProductPeriodField(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="period")

    period = models.TextField('Период годов (от-до)', blank=True)
    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Период товара'
        verbose_name_plural = "Пеироды товаоров"
        ordering = ["my_order"]


class ProductMaterialField(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="material")

    material = models.TextField('Материал продукта', blank=True)
    material_eng = models.TextField('Материал продукта (на аннгл)', blank=True)
    material_uzb = models.TextField('Материал продукта (на узб)', blank=True)
    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Материал товара товара'
        verbose_name_plural = "Материалы товара товаоров"
        ordering = ["my_order"]

class ProductSizeField(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="size")

    size = models.CharField(max_length=128, verbose_name='Размер продукта', blank=True)
    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Размер товара'
        verbose_name_plural = "Размеры товаров "
        ordering = ["my_order"]


class ProductConditionField(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="condition")

    condition = models.CharField(max_length=256, verbose_name='Состояние продукта', blank=True)
    condition_eng = models.CharField(max_length=256, verbose_name='Состояние продукта (на англ)', blank=True)
    condition_uz = models.CharField(max_length=256, verbose_name='Состояние продукта (на узб)', blank=True)
    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Состояние товара'
        verbose_name_plural = "Состояние товаров товаров товаоров"
        ordering = ["my_order"]

class ProductStatusField(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="status")

    status = models.CharField(max_length=256, verbose_name='Товар в единственном экземпляре или нет', blank=True)
    status_eng = models.CharField(max_length=256, verbose_name='Товар в единственном экземпляре или нет (на англ)', blank=True)
    status_uz = models.CharField(max_length=256, verbose_name='Товар в единственном экземпляре или нет (на узб)', blank=True)
    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Статус товара'
        verbose_name_plural = "Статус товара"
        ordering = ["my_order"]

class ArtProductAuthorField(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="author")

    author = models.CharField(max_length=256, verbose_name='Имя художника', blank=True)
    author_eng = models.CharField(max_length=256, verbose_name='Имя художника (на англ)', blank=True)
    author_uz = models.CharField(max_length=256, verbose_name='Имя художника (на узб)', blank=True)
    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Автор товара'
        verbose_name_plural = "Авторы товара"
        ordering = ["my_order"]


class ArtProductYearField(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="year")

    year = models.CharField(max_length=128, verbose_name='Год выпуска', blank=True, null=True)
    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Год товара'
        verbose_name_plural = "Годы товара"
        ordering = ["my_order"]


class ArtProductTechniqueField(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="technique")

    technique = models.TextField('Техника', blank=True)
    technique_eng = models.TextField('Техника (на англ)', blank=True)
    technique_uz = models.TextField('Техника (на узб)', blank=True)
    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Год товара'
        verbose_name_plural = "Годы товара"
        ordering = ["my_order"]


class ProductImage(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="image")

    image = models.ImageField(upload_to='media', verbose_name='Фото продукта')

    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,

    )

    class Meta:
        verbose_name="Фото товара"
        verbose_name_plural="Фотки товара"
        ordering = ['my_order']




class Workers(models.Model):
    name = models.CharField(max_length=128, verbose_name='Имя сотрудника')
    name_eng = models.CharField(max_length=128, verbose_name='Имя сотрудника (на англ)', default="")
    name_uz = models.CharField(max_length=128, verbose_name='Имя сотрудника (на узб)', default="")
    description = models.TextField('Описание для сотрудника')
    description_eng = models.TextField('Описание для сотрудника (на англ)', default="")
    description_uz = models.TextField('Описание для сотрудника (на узб)', default="")
    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['my_order']

    def __str__(self):
        return self.name



class WorkersImage(models.Model):
    worker = models.ForeignKey(Workers, on_delete=models.CASCADE, related_name="image")

    image = models.ImageField(upload_to='media', verbose_name='Фото рабочего')

    my_order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )

    class Meta:
        verbose_name = "Фото рабочего"
        verbose_name_plural = "Фотки рабочего"
        ordering = ['my_order']


class Cart(models.Model):
    session_key = models.TextField('Секретный ключ. НЕ ТРОГАТЬ ЭТОТ ОБЬЕКТ')
    user_product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True)
    user_event = models.ForeignKey(Events, on_delete=models.CASCADE, null=True)
    user_masterclass = models.ForeignKey(Masterclasses, on_delete=models.CASCADE, null=True)
    choosed_amount = models.IntegerField(default=0)

    def calculate_final_product_price(self):
        product_price = int(self.user_product.price) if int(self.user_product.price) > 0 else False
        product_price_eur = int(self.user_event.price_eur) if int(self.user_product.price_eur) > 0 else False
        product_price_usd = int(self.user_event.price_usd) if int(self.user_product.price_usd) > 0 else False
        positive_quantity = self.choosed_amount if self.choosed_amount > 0 else False
        if product_price:
            calculated_price = product_price * positive_quantity
            return calculated_price
        elif product_price_eur:
            calculated_price = product_price_eur * positive_quantity
            return calculated_price
        elif product_price_usd:
            calculated_price = product_price_usd * positive_quantity
            return calculated_price
        else:
            return False

    def calculate_event_price(self):
        event_price = int(self.user_event.price) if int(self.user_event.price) > 0 else False
        event_price_eur = int(self.user_event.price_eur) if int(self.user_event.price_eur) > 0 else False
        event_price_usd = int(self.user_event.price_usd) if int(self.user_event.price_usd) > 0 else False
        positive_quantity = self.choosed_amount if self.choosed_amount > 0 else False
        if event_price:
            calculated_price = event_price * positive_quantity
            return calculated_price
        elif event_price_eur:
            calculated_price = event_price * positive_quantity
            return calculated_price
        if event_price_usd:
            calculated_price = event_price * positive_quantity
            return calculated_price
        else:
            return False

    def count_price_masterclass(self):
        masterclass_price = int(self.user_masterclass.price) if int(self.user_masterclass.price) > 0 else False
        masterclass_price_eur = int(self.user_masterclass.price_eur) if int(self.user_masterclass.price_eur) > 0 else False
        masterclass_price_usd = int(self.user_masterclass.price_usd) if int(self.user_masterclass.price_usd) > 0 else False
        positive_quantity = self.choosed_amount if self.choosed_amount > 0 else False
        if masterclass_price:
            calculated_price = masterclass_price * positive_quantity
            return calculated_price
        elif masterclass_price_eur:
            calculated_price = masterclass_price_eur * positive_quantity
            return calculated_price
        if masterclass_price_usd:
            calculated_price = masterclass_price_usd * positive_quantity
            return calculated_price
        else:
            return False



    class Meta:
        verbose_name = 'Корзина'

    def __str__(self):
        return 'Товар добавлен в корзину'
