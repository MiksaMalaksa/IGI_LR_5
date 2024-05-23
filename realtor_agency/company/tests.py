from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from agency.models import Employer, Property, Sale, Category
from .models import Article, CompanyInfo, Dictionary, Contact, Vacancy, Review, Coupon


class ArticleModelTest(TestCase):

    def setUp(self):
        self.article = Article.objects.create(
            title="Test Article",
            content="This is a test article.",
            published_at=timezone.now()
        )

    def test_article_creation(self):
        self.assertEqual(self.article.title, "Test Article")
        self.assertEqual(self.article.content, "This is a test article.")
        self.assertTrue(self.article.published_at)

    def test_article_str(self):
        self.assertEqual(str(self.article), "Test Article")


class CompanyInfoModelTest(TestCase):

    def setUp(self):
        self.company_info = CompanyInfo.objects.create(information="This is company information.")

    def test_company_info_creation(self):
        self.assertEqual(self.company_info.information, "This is company information.")

    def test_company_info_str(self):
        self.assertEqual(str(self.company_info), "Company Info")


class DictionaryModelTest(TestCase):

    def setUp(self):
        self.dictionary = Dictionary.objects.create(
            term="Test Term",
            definition="This is a test definition.",
            added_at=timezone.now()
        )

    def test_dictionary_creation(self):
        self.assertEqual(self.dictionary.term, "Test Term")
        self.assertEqual(self.dictionary.definition, "This is a test definition.")
        self.assertTrue(self.dictionary.added_at)

    def test_dictionary_str(self):
        self.assertEqual(str(self.dictionary), "Test Term")


class ContactModelTest(TestCase):

    def setUp(self):
        self.employer = Employer.objects.create(
            first_name="John",
            last_name="Doe",
            phone_number="+375 (29) 123-45-67",
            email="john.doe@example.com"
        )
        self.contact = Contact.objects.create(
            employer=self.employer,
            description="Contact description.",
        )

    def test_contact_creation(self):
        self.assertEqual(self.contact.employer, self.employer)
        self.assertEqual(self.contact.description, "Contact description.")

    def test_contact_str(self):
        self.assertEqual(str(self.contact), "John")


class VacancyModelTest(TestCase):

    def setUp(self):
        self.vacancy = Vacancy.objects.create(
            title="Test Vacancy",
            description="This is a test vacancy.",
            salary=50000.00,
            experience_required=5
        )

    def test_vacancy_creation(self):
        self.assertEqual(self.vacancy.title, "Test Vacancy")
        self.assertEqual(self.vacancy.description, "This is a test vacancy.")
        self.assertEqual(self.vacancy.salary, 50000.00)
        self.assertEqual(self.vacancy.experience_required, 5)

    def test_vacancy_str(self):
        self.assertEqual(str(self.vacancy), "Test Vacancy")


class ReviewModelTest(TestCase):

    def setUp(self):
        self.review = Review.objects.create(
            name="John Doe",
            rating=5,
            text="Great service!",
            created_at=timezone.now()
        )

    def test_review_creation(self):
        self.assertEqual(self.review.name, "John Doe")
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.text, "Great service!")
        self.assertTrue(self.review.created_at)

    def test_review_str(self):
        self.assertEqual(str(self.review), "John Doe - 5")


class CouponModelTest(TestCase):

    def setUp(self):
        self.coupon = Coupon.objects.create(
            code="DISCOUNT2023",
            active=True
        )

    def test_coupon_creation(self):
        self.assertEqual(self.coupon.code, "DISCOUNT2023")
        self.assertTrue(self.coupon.active)

    def test_coupon_str(self):
        self.assertEqual(str(self.coupon), "DISCOUNT2023")


class PropertyModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Residential")
        self.employer = Employer.objects.create(
            first_name="John",
            last_name="Doe",
            phone_number="+375 (29) 123-45-67",
            email="john.doe@example.com"
        )
        self.property = Property.objects.create(
            title="Test Property",
            price=250000.00,
            location="123 Main St",
            floor=5,
            square_meters=150.50,
            owner=self.employer,
        )
        self.property.property_types.add(self.category)

    def test_property_creation(self):
        self.assertEqual(self.property.title, "Test Property")
        self.assertEqual(self.property.price, 250000.00)
        self.assertEqual(self.property.location, "123 Main St")
        self.assertEqual(self.property.floor, 5)
        self.assertEqual(self.property.square_meters, 150.50)
        self.assertEqual(self.property.owner, self.employer)
        self.assertIn(self.category, self.property.property_types.all())

    def test_property_str(self):
        self.assertEqual(str(self.property), "Test Property")


