from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import phonenumbers

from django.http import JsonResponse
from django.templatetags.static import static

from .models import Product, Order, OrderProduct


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    order_raw = request.data
    print(order_raw)
    try:
        assert isinstance(order_raw['products'], list)
    except KeyError:
        return Response(
            {'error': 'products: Обязательное поле'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except AssertionError:
        return Response(
            {'error': 'products: Ожидался list со значениями'},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    try:
        if not all([order_raw['firstname'], order_raw['lastname'], order_raw['phonenumber'], order_raw['address']]):
            return Response(
                {'error': 'firstname, lastname, phonenumber, address: Это поле не может быть пустым'},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except KeyError:
        return Response(
            {'error': 'firstname, lastname, phonenumber, address: Обязательное поле'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not isinstance(order_raw['firstname'], str):
        return Response(
            {'error': 'firstname: Not a valid string.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        phonenumber = phonenumbers.parse(order_raw['phonenumber'])
    except phonenumbers.NumberParseException as err:
        return Response(
            {'error': err},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not phonenumbers.is_valid_number(phonenumber):
        return Response(
            {'error': 'phonenumber: Введен некорректный номер телефона'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if order_raw.get('products'):
        order = Order.objects.create(firstname=order_raw['firstname'],
                                     lastname=order_raw['lastname'],
                                     phonenumber=order_raw['phonenumber'],
                                     address=order_raw['address'],
                                     )
        for order_item in order_raw['products']:
            try:
                product = Product.objects.get(pk=order_item['product'])
            except Product.DoesNotExist:
                return Response(
                    {'error': f'products: Недопустимый первичный ключ {order_item["product"]}'}
                )
            OrderProduct(product=product,
                         quantity=order_item['quantity'],
                         order=order,
                         ).save()
        return Response(
            {'status': 'OK'},
            status=status.HTTP_200_OK,
        )
    return Response(
        {'error': 'products: Этот список не может быть пустым'},
        status=status.HTTP_400_BAD_REQUEST,
    )
