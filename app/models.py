from django.db import models



class News(models.Model):
    photo = models.ImageField(upload_to='media', verbose_name='Фото для новости')
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    date = models.DateField('Дата')
    description = models.TextField('Описание')
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



class Masterclasses(models.Model):
    photo = models.ImageField(upload_to='media', verbose_name='Фото мероприятия', default='')
    name = models.CharField(max_length=128, verbose_name='Название мастеркласса')
    tamada = models.CharField(max_length=128, verbose_name='Ведущий')
    date = models.DateField('Дата мастеркалсса')
    time = models.TimeField('Время мастеркласса')
    desc = models.TextField('Описание')
    price = models.IntegerField('Цена')
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







class Feedbacks(models.Model):
    text = models.TextField('Текст отзыва')
    author_name = models.CharField('Имя автора отзыва', max_length=128, blank=True)
    author_role = models.CharField('Род деятельности автора', max_length=128, blank=True)
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
    photo_of_event = models.ImageField(upload_to='media', verbose_name='Фото ивента')
    desc = models.TextField('Описание')
    allowed_amount = models.IntegerField(default=0, verbose_name='Доступно мест')
    place_abilities = models.TextField('Возмонжости пространства')
    extra_service = models.TextField(null=True, verbose_name='Доп услуги')
    price = models.IntegerField(verbose_name='Цена за место', default=0)
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


class ProductCategory(models.Model):
    category_name = models.CharField(max_length=128, verbose_name='Название категории')
    cover_photo = models.ImageField(
        upload_to='media',
        blank=True,
        null=True,
        verbose_name='Фото-баннер категории',
        help_text='Если не загружено — на сайте показывается фото галереи по умолчанию',
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
    photo1 = models.ImageField(upload_to='media', verbose_name='Фото 1', blank=True, null=True)
    photo2 = models.ImageField(upload_to='media', verbose_name='Фото 2', blank=True, null=True)
    photo3 = models.ImageField(upload_to='media', verbose_name='Фото 3', blank=True, null=True)
    photo4 = models.ImageField(upload_to='media', verbose_name='Фото 4', blank=True, null=True)
    photo5 = models.ImageField(upload_to='media', verbose_name='Фото 5', blank=True, null=True)
    photo6 = models.ImageField(upload_to='media', verbose_name='Фото 6', blank=True, null=True)
    price = models.CharField(max_length=128, verbose_name='Цена')
    allowed_amount = models.IntegerField(default=0, verbose_name='Доступно продуктов')
    desc = models.TextField('Описание продукта')
    details = models.TextField('Особенности кроя и отделки')
    carry = models.TextField('Рекомендации по уходу')


    # Доп поля для secondhand, vintage, retail


    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, default='')
    period = models.TextField('Период годов (от-до)', blank=True)
    material = models.TextField('Материал продукта', blank=True)
    size = models.CharField(max_length=128, verbose_name='Размер продукта', blank=True)
    condition = models.CharField(max_length=256, verbose_name='Состояние продукта', blank=True)
    status = models.CharField(max_length=256, verbose_name='Товар в единственном экземпляре или нет')

    # Доп поля для art


    author = models.CharField(max_length=256, verbose_name='Имя художника', blank=True)
    year = models.CharField(max_length=128, verbose_name='Год выпуска', blank=True, null=True)
    technique = models.TextField('Техника', blank=True)
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







class Workers(models.Model):
    photo = models.ImageField(upload_to='media', verbose_name='Фото сотрудника')
    name = models.CharField(max_length=128, verbose_name='Имя сотрудника')
    description = models.TextField('Описание для сотрудника')
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



class Cart(models.Model):
    session_key = models.TextField('Секретный ключ. НЕ ТРОГАТЬ ЭТОТ ОБЬЕКТ')
    user_product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True)
    user_event = models.ForeignKey(Events, on_delete=models.CASCADE, null=True)
    user_masterclass = models.ForeignKey(Masterclasses, on_delete=models.CASCADE, null=True)
    user_amount = models.IntegerField(default=0)

    def count_price_product(self):
        user_pr_price = int(self.user_product.price)
        if self.user_amount != 0:
            user_final_price = user_pr_price * self.user_amount
            return user_final_price
        else:
            return False


    def count_price_event(self):
        user_ev_price = int(self.user_event.price)
        if self.user_amount != 0:
            user_final_price = user_ev_price * self.user_amount
            return user_final_price
        else:
            return False

    def count_price_masterclass(self):
        user_masterclass_price = int(self.user_masterclass.price)
        if self.user_amount != 0:
            user_final_price = user_masterclass_price * self.user_amount
            return user_final_price
        else:
            return False



    class Meta:
        verbose_name = 'Корзина'

    def __str__(self):
        return 'Товар добавлен в корзину'
