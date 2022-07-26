from ..forms import *
from .base_views import *
import json
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse


class CartProduct:
    def __init__(self, product_id, name, price, count, **kwargs):
        self.product_id = product_id
        self.name = name
        self.count = count
        self.price = price
        self.total = self.price * self.count

    @classmethod
    def from_json(cls, json_string):
        json_dict = json.loads(json_string)
        return cls(**json_dict)

    @classmethod
    def from_dict(cls, dictionary):
        return cls(**dictionary)

    def to_dict(self):
        return self.__dict__


class Cart:
    def __init__(self, restaurant_id, address_id, products, total, **kwargs):
        self.restaurant_id = restaurant_id
        self.address_id = address_id
        self.products = []
        self.total = total
        for product in products:
            self.products.append(CartProduct.from_dict(product))

    def find(self, product_id):
        products = list(filter(lambda x: x.product_id == product_id, self.products))

        if len(products) >= 1:
            return products[0]
        else:
            return None

    def append(self, product, count=1):
        self.set_restaurant(product.restaurant)

        cart_product = self.find(product.id)
        if cart_product is None:
            cart_product = CartProduct(product.id, product.name, product.price, count)
            self.products.append(cart_product)
        else:
            cart_product.name = product.name
            cart_product.count = cart_product.count + count

        if cart_product.count <= 0:
            self.products.remove(cart_product)

    def remove(self, product_id):
        product = self.find(product_id)
        if product is not None:
            self.products.remove(product)

    def set_restaurant(self, restaurant):
        if restaurant.id != self.restaurant_id:
            self.clear()
            self.restaurant_id = restaurant.id

    def set_address(self, address):
        self.set_restaurant(address.restaurant)
        self.address_id = address.id

    def clear(self):
        self.products = []

    @classmethod
    def load(cls, request):
        cart = request.session.get('cart', Cart(None, None, [], 0).to_dict())
        return Cart.from_dict(cart)

    def save(self, request):
        self.total = sum([product.count * product.price for product in self.products])
        request.session['cart'] = self.to_dict()

    @classmethod
    def from_json(cls, json_string):
        json_dict = json.loads(json_string)
        return cls(**json_dict)

    @classmethod
    def from_dict(cls, dictionary):
        return cls(**dictionary)

    def to_dict(self):
        products = []
        products_ids = []

        for product in self.products:
            products_ids.append(product.product_id)
            products.append(product.to_dict())

        return {'restaurant_id': self.restaurant_id, 'address_id': self.address_id, 'products_ids': products_ids,
                'products': products, 'total': self.total}


class CartViewComponent(View):
    template_name = 'base/cart.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class CartCheckoutViewComponent(View):
    template_name = 'base/cart_checkout.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class CartAdd(View):

    def get(self, request, product_id, count, *args, **kwargs):
        cart = Cart.load(request)

        product = get_object_or_404(Product, id=product_id)

        cart.append(product, count)
        cart.save(request)
        return redirect('cart_view')


class CartDelete(View):

    def get(self, request, product_id, count, *args, **kwargs):
        cart = Cart.load(request)

        product = get_object_or_404(Product, id=product_id)

        cart.append(product, -count)
        cart.save(request)
        return redirect('cart_view')


class CartRemove(View):

    def get(self, request, product_id, *args, **kwargs):
        cart = Cart.load(request)

        product = get_object_or_404(Product, id=product_id)

        cart.remove(product.id)
        cart.save(request)
        return redirect('cart_view')


class CartClear(View):

    def get(self, request):
        cart = Cart.load(request)
        cart.clear()
        cart.save(request)
        return redirect('cart_view')


class CartSetAddress(View):

    def get(self, request, *args, **kwargs):
        address_id = request.GET.get('address', None)
        cart = Cart.load(request)
        cart.set_address(get_object_or_404(AddressOfRestaurant, id=address_id))
        cart.save(request)
        return HttpResponse()


