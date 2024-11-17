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

class Certificate(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))  # Название сертификата
    subtitle = models.CharField(max_length=255, verbose_name=_("Subtitle"), blank=True, null=True)  # Подзаголовок
    company_name = models.CharField(max_length=255, verbose_name=_("Company Name"))  # Название компании
    date_issued = models.DateField(default=timezone.now, verbose_name=_("Date Issued"))  # Дата выдачи
    registry_number = models.CharField(max_length=50, verbose_name=_("Registry Number"))  # Реестровый номер
    logo = models.ImageField(upload_to='certificates/', blank=True, null=True, verbose_name=_("Logo"))  # Логотип сертификата
    certificate_footer = models.TextField(verbose_name=_("Footer Text"), blank=True, null=True)  # Подпись или футер сертификата
    certificate_image = models.ImageField(upload_to='certificates/images/', blank=True, null=True, verbose_name=_("Certificate Image"))  # Картинка сертификата
    signature_image = models.ImageField(upload_to='certificates/signatures/', blank=True, null=True, verbose_name=_("Signature Image"))  # Картинка подписи

    class Meta:
        verbose_name = _("Certificate")
        verbose_name_plural = _("Certificates")

    def __str__(self):
        return self.title

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

class CompanyInfo(models.Model):
    information = models.TextField(verbose_name=_("Information"))
    video_url = models.URLField(blank=True, null=True, verbose_name=_("Video URL"))
    logo = models.ImageField(upload_to='logos/', blank=True, null=True, verbose_name=_("Logo"))
    history = models.TextField(blank=True, null=True, verbose_name=_("History"))
    requisites = models.TextField(blank=True, null=True, verbose_name=_("Requisites"))
    
    # Связь с сертификатом
    certificate = models.ForeignKey(Certificate, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Certificate"))

    class Meta:
        verbose_name = _("Company Info")
        verbose_name_plural = _("Company Info")

    def __str__(self):
        return "Company Info"




class Sponsor(models.Model):
    name = models.CharField(max_length=255)
    logo = models.CharField(max_length=255)  # This stores the relative path to the logo in static
    website = models.URLField()

    class Meta:
        verbose_name = _("sponsor")
        verbose_name_plural = _("sponsors")

    def __str__(self):
        return self.name

    # Method to get the logo path using static URL
    def get_logo_path(self):
        return f"images/{self.logo}"

class Contact(models.Model):
    employer = models.ForeignKey(
        Employer, on_delete=models.CASCADE, default=None)
    description = models.TextField()
    image = models.ImageField(upload_to="contacts/", null=True, blank=True)
    website = models.URLField(blank=True, null=True)  # Добавлено поле website

    class Meta:
        verbose_name = _("contact")
        verbose_name_plural = _("contacts")

    def __str__(self):
        return f"{self.employer.first_name} {self.employer.last_name}" if self.employer else 'No Employer'



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
