from phonenumber_field.modelfields import PhoneNumberField

from django.core.validators import MinValueValidator

from django.db import models
from django.db.models import F, Sum


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
                .filter(availability=True)
                .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=500,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def annotate_order_cost(self):
        cost_of_product = F('orderproduct__price_fixed') * F('orderproduct__quantity')
        return self.annotate(order_cost=Sum(cost_of_product))


class Order(models.Model):
    firstname = models.CharField(
        'Имя',
        max_length=250,
        db_index=True,
    )
    lastname = models.CharField(
        'Фамилия',
        max_length=250,
        db_index=True,
    )
    phonenumber = PhoneNumberField(
        'Номер телефона',
        db_index=True,
    )
    address = models.TextField(verbose_name='Адрес')
    order_items = models.ManyToManyField(
        Product,
        verbose_name='Позиция в заказе',
        through='OrderProduct',
        related_name='orders',
    )
    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.pk} {self.firstname}, {self.address}'


class OrderProduct(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name='Товар',
        on_delete=models.CASCADE,
    )
    order = models.ForeignKey(
        Order,
        verbose_name='Номер заказа',
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField('Количество товара')
    price_fixed = models.DecimalField(
        'Цена на момент заказа',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]

    )

    class Meta:
        verbose_name = 'Позиции заказов'
        verbose_name_plural = 'Позиции заказов'

    def __str__(self):
        return f'#{self.order.pk} order: {self.product} × {self.quantity}'
