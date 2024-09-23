from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from agency.models import Employer
from django import forms


class BaseModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to="articles/", null=True, blank=True)
    published_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("article")
        verbose_name_plural = _("articles")

    def __str__(self):
        return self.title

class CompanyInfo(models.Model):
    information = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    history = models.TextField(blank=True, null=True)
    requisites = models.TextField(blank=True, null=True)
    certificate = models.ImageField(upload_to='certificates/', blank=True, null=True) 
    certificate_text = models.CharField(max_length=50)

    class Meta:
        verbose_name = _("company info")
        verbose_name_plural = _("company info")

    def __str__(self):
        return "Company Info"


class Dictionary(models.Model):
    term = models.CharField(max_length=255)  # Question or term
    definition = models.TextField()  # Brief answer or definition
    expanded_answer = models.TextField(blank=True, null=True)  # Detailed answer
    is_frequently_asked = models.BooleanField(default=False)  # FAQ indicator
    added_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("dictionary")
        verbose_name_plural = _("dictionary")

    def __str__(self):
        return self.term


class Contact(models.Model):
    employer = models.ForeignKey(
        Employer, on_delete=models.CASCADE, default=None)
    description = models.TextField()
    image = models.ImageField(upload_to="contacts/", null=True, blank=True)

    class Meta:
        verbose_name = _("contact")
        verbose_name_plural = _("contacts")

    def __str__(self):
        return self.employer.first_name if self.employer else 'No Employer'


class Vacancy(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    experience_required = models.IntegerField()

    class Meta:
        verbose_name = _("vacancy")
        verbose_name_plural = _("vacancies")

    def __str__(self):
        return self.title

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"), default=1)  # Set a default user ID
    name = models.CharField(max_length=255)
    rating = models.PositiveSmallIntegerField()
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("review")
        verbose_name_plural = _("reviews")

    def __str__(self):
        return f"{self.user.username} - {self.rating}"
    
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }


class Coupon(models.Model):
    code = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)
    discount_amount = models.IntegerField(default=0)

    class Meta:
        verbose_name = _("coupon")
        verbose_name_plural = _("coupons")

    def __str__(self):
        return self.code
