import os
from django import forms
from django.views import View
from django.shortcuts import render, redirect

from ..models import *


class Index(View):
    template_name = 'main/index.html'

    def get(self, request, *args, **kwargs):
        all_restaurants = Restaurant.get_active_restaurants()
        restaurants = None
        bad_query = None

        category_id = request.GET.get('category', None)

        if category_id is None:
            restaurants = all_restaurants
        else:
            try:
                category_id = int(category_id)
                restaurants = all_restaurants.filter(categories__id=category_id)
                if restaurants.count() <= 0:
                    bad_query = True
                    restaurants = all_restaurants
            except:
                restaurants = all_restaurants

        context = {'restaurants': restaurants, 'categories': RestaurantCategory.objects.all(),
                   'selected_category_id': category_id, 'bad_query': bad_query}
        return render(request, self.template_name, context)


class Search(View):
    template_name = 'main/search.html'

    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '')

        restaurants = []

        result = []
        text = None

        if len(query) > 2:
            restaurants = list(Restaurant.objects.filter(title__icontains=query))
            products = Product.objects.filter(name__icontains=query)

            for product in products:
                if product.restaurant not in restaurants:
                    restaurants.append(product.restaurant)

            for restaurant in restaurants:
                rest_products = products.filter(restaurant=restaurant)
                result.append({'restaurant': restaurant, 'products': rest_products})
        else:
            text = 'Введите минимум 3 символа'

        context = {'result': result, 'text': text}

        return render(request, self.template_name, context)


class Welcome(View):
    template_name = 'welcome.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
