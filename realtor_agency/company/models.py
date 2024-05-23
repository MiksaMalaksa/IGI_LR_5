from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# from realtor_agency.agency.models import Employer
from agency.models import Employer


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

    class Meta:
        verbose_name = _("company info")
        verbose_name_plural = _("company info")

    def __str__(self):
        return "Company Info"


class Dictionary(models.Model):
    term = models.CharField(max_length=255)
    definition = models.TextField()
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
    name = models.CharField(max_length=255)
    rating = models.PositiveSmallIntegerField()
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("review")
        verbose_name_plural = _("reviews")

    def __str__(self):
        return f"{self.name} - {self.rating}"


class Coupon(models.Model):
    code = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)
    discount_amount = models.IntegerField(default=0)

    class Meta:
        verbose_name = _("coupon")
        verbose_name_plural = _("coupons")

    def __str__(self):
        return self.code
