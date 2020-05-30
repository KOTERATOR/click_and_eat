from django import forms
from django.forms import ModelForm
from .models import *
import datetime


class CategoryModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.title


class AddressModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.address


class RestaurantCategoryModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.title


class RestaurantCategoryModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.title


class LoginForm(forms.Form):
    username = forms.CharField(max_length=12)
    password = forms.CharField(widget=forms.PasswordInput())
    remember_me = forms.BooleanField(required=False)


class RegisterForm(LoginForm):
    first_name = forms.CharField(max_length=12)
    email = forms.EmailField()
    repeat_password = forms.CharField(widget=forms.PasswordInput())


class UserEditForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']


class RestaurantEditForm(ModelForm):
    class Meta:
        model = Restaurant
        fields = ['title', 'description', 'logo', 'preview_image', 'open_time', 'close_time', 'main_category',
                  'categories']
        field_classes = {'main_category': RestaurantCategoryModelChoiceField,
                         'categories': RestaurantCategoryModelMultipleChoiceField}
        widgets = {
            'main_category': forms.Select(attrs={'class': 'uk-select'}),
            'categories': forms.SelectMultiple(attrs={'class': 'uk-select'})
        }


class RestaurantAddProductForm(ModelForm):
    def set_restaurant(self, restaurant):
        self.fields['category'].queryset = Category.objects.filter(restaurant=restaurant)

    class Meta:
        model = Product
        fields = ['name', 'description', 'photo', 'price', 'value', 'category']
        field_classes = {'category': CategoryModelChoiceField}
        widgets = {
            'category': forms.Select(attrs={'class': 'uk-select'}),
        }


class RestaurantAddCategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['title']


class RestaurantAddressForm(ModelForm):
    class Meta:
        model = AddressOfRestaurant
        fields = ['address', 'longitude', 'latitude']


class CheckoutForm(forms.Form):
    pickup_time = forms.DateTimeField()
    instant = forms.BooleanField(required=False)
    comment = forms.CharField(max_length=512, required=False)

    def set_restaurant(self, restaurant, address=None):
        self.fields['instant'].widget = forms.CheckboxInput(attrs={'class': 'uk-checkbox'})
        self.fields['pickup_time'].widget = forms.DateTimeInput(attrs={'class': 'uk-input uk-border'})
        self.fields['pickup_time'].initial = datetime.datetime.now() + datetime.timedelta(minutes=15)
        self.fields['comment'].widget = forms.TextInput(attrs={'class': 'uk-textarea'})


class OrderFinishForm(forms.Form):
    secret_code = forms.IntegerField()
