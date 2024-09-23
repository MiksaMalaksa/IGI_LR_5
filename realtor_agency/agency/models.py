from django.contrib.auth.models import User
from django.db import models
from django.core.validators import (
    MinValueValidator,
    RegexValidator,
    MaxValueValidator,
    MinLengthValidator,
    MaxLengthValidator,
)
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthdate = models.DateField()

    def __str__(self):
        return self.user.username

    def age(self):
        today = date.today()
        return today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Employer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    job = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=255, blank=True, validators=[
        RegexValidator(r"\+375 \((29|33|25)\) \d{3}-\d{2}-\d{2}"),
        MinLengthValidator(19), MaxLengthValidator(19)
    ])
    email = models.EmailField()

    @staticmethod
    def get_default_owner():
        owner, created = Employer.objects.get_or_create(
            first_name='Miksa',
            last_name='Miksailovich',
            defaults={'phone_number': '+375 (29) 660 3741', 'email': 'malaxa2000@gmail.com'}
        )
        return owner

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Property(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    floor = models.IntegerField()
    square_meters = models.DecimalField(max_digits=7, decimal_places=2)
    owner = models.ForeignKey(Employer, on_delete=models.SET_DEFAULT, default=Employer.get_default_owner, related_name='properties')
    property_types = models.ManyToManyField(Category, related_name='properties')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='property_images/', blank=True)

    def __str__(self):
        return f"{self.title} - {self.location}"

    def purchase(self, user, coupons=[]):
        if len(coupons) > 2:
            raise ValidationError("You can apply a maximum of 2 coupons.")

        total_discount = sum(10 for coupon in coupons if coupon.active)
        final_price = self.price - total_discount
        if final_price < 0:
            raise ValidationError("Total discount exceeds property price.")

        sale = Sale.objects.create(
            property=self,
            buyer=user,
            sale_date=timezone.now().date(),
            contract_date=timezone.now().date(),
            sale_price=final_price
        )
        return sale


class Sale(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='sales')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    sale_date = models.DateField()
    employee = models.ForeignKey(Employer, on_delete=models.SET_NULL, null=True, related_name='sales')
    contract_date = models.DateField()
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Sale of {self.property.title} to {self.buyer.username}'


class Cart(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='cart')
    properties = models.ManyToManyField(Property, through='CartItem', related_name='carts')

    def __str__(self):
        return f"Cart of {self.user.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.property.title} in cart of {self.cart.user.user.username}"
