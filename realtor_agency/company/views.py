from datetime import date, datetime
import json
import re
from django.forms import ValidationError
from django.http import JsonResponse
from .models import Contact
from .forms import ContactForm, ReviewForm, PropertyForm
import logging
import requests
from agency.models import Employer, Property, Sale, Cart, CartItem, User, Profile
from django.db.models import Avg, Max, Count, Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .utils import get_user_time
from company.models import Article, CompanyInfo, Dictionary, Vacancy, Review, Coupon, Sponsor
from django.contrib import admin
import requests
from django.core.files.base import ContentFile
from urllib.parse import urlparse
import os
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

@login_required  
def get_contacts(request):
    if request.method == 'GET':
        contacts = Contact.objects.all().select_related('employer').values(
            'id',
            'employer__first_name',
            'employer__last_name',
            'employer__job',
            'employer__phone_number',
            'employer__email',
            'description',
            'image',
            'website', 
        )
        contacts_list = list(contacts)
        for contact in contacts_list:
            if contact['image']:
                contact['image'] = request.build_absolute_uri(contact['image'])
            else:
                contact['image'] = ''  
        return JsonResponse({'contacts': contacts_list})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

@login_required 
def add_contact(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            job_description = data.get('job_description', '').strip()
            phone_number = data.get('phone_number', '').strip()
            email = data.get('email', '').strip()
            website = data.get('website', '').strip()
            photo_url = data.get('photo', '').strip()

            # Валидация обязательных полей
            if not all([first_name, last_name, job_description, phone_number, email]):
                return JsonResponse({'success': False, 'error': 'All fields except website are required.'}, status=400)

            # Валидация URL для website
            url_pattern = re.compile(r'^(http:\/\/|https:\/\/).*\.(php|html)$')
            if website and not url_pattern.match(website):
                return JsonResponse({'success': False, 'error': 'Invalid Website URL format.'}, status=400)

            # Валидация номера телефона
            phone_pattern = re.compile(r'^(\+375|8)\s?\(?\d{2}\)?\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}$')
            if not phone_pattern.match(phone_number):
                return JsonResponse({'success': False, 'error': 'Invalid phone number format.'}, status=400)

            # Создание или получение объекта Employer
            employer, created = Employer.objects.get_or_create(
                first_name=first_name,
                last_name=last_name,
                job=job_description,
                phone_number=phone_number,
                email=email
            )

            # Обработка изображения по URL
            image_file = None
            if photo_url:
                try:
                    response = requests.get(photo_url)
                    if response.status_code == 200:
                        parsed_url = urlparse(photo_url)
                        filename = os.path.basename(parsed_url.path)
                        image_content = ContentFile(response.content)
                        image_file = ContentFile(image_content.read(), name=filename)
                    else:
                        return JsonResponse({'success': False, 'error': 'Failed to download image from URL.'}, status=400)
                except Exception as e:
                    return JsonResponse({'success': False, 'error': f'Error downloading image: {str(e)}'}, status=400)

            # Создание нового контакта
            contact = Contact.objects.create(
                employer=employer,
                description=job_description,
                website=website  # Предполагается, что в модели Contact есть поле 'website'
            )

            # Сохранение изображения, если оно было загружено
            if image_file:
                contact.image.save(image_file.name, image_file, save=True)

            return JsonResponse({'success': True, 'contact': {
                'id': contact.id,
                'first_name': contact.employer.first_name,
                'last_name': contact.employer.last_name,
                'job_description': contact.employer.job,
                'phone_number': contact.employer.phone_number,
                'email': contact.employer.email,
                'description': contact.description,
                'website': contact.website,
                'image': contact.image.url if contact.image else '',
            }})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)

@login_required  
def reward_contacts(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            contact_ids = data.get('contact_ids', [])

            if not contact_ids:
                return JsonResponse({'success': False, 'error': 'No contacts selected for reward.'}, status=400)

            contacts = Contact.objects.filter(id__in=contact_ids).select_related('employer')
            if not contacts.exists():
                return JsonResponse({'success': False, 'error': 'No valid contacts found.'}, status=400)

            names = [f"{contact.employer.first_name} {contact.employer.last_name}" for contact in contacts]

            # Создание текста премирования
            reward_text = f"Congratulations to: {', '.join(names)} for their well-deserved reward!"

            return JsonResponse({'success': True, 'reward_text': reward_text})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=400)


@login_required
def add_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your review has been submitted!')
            return redirect('reviews')  # Adjust this to your reviews list view
    else:
        form = ReviewForm()

    return render(request, 'add_review.html', {'form': form})


def reviews(request):
    all_reviews = Review.objects.all()
    return render(request, 'reviews.html', {'reviews': all_reviews})

def html_demo(request):
    return render(request, 'html_demo.html')

@login_required
def cart_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    cart, created = Cart.objects.get_or_create(user=profile)
    cart_items = CartItem.objects.filter(cart=cart)

    total_price = sum(item.property.price * item.quantity for item in cart_items)
    
    # Handle cart actions if needed (e.g., updates, removals)
    if request.method == 'POST':
        for item in cart_items:
            if f'increase_{item.property.id}' in request.POST:
                item.quantity += 1
                item.save()
            elif f'decrease_{item.property.id}' in request.POST and item.quantity > 1:
                item.quantity -= 1
                item.save()
            elif f'remove_{item.property.id}' in request.POST:
                item.delete()

        return redirect('cart')

    context = {'cart_items': cart_items, 'total_price': total_price}
    return render(request, 'cart.html', context)

@login_required
def add_to_cart(request, property_id):
    property_item = get_object_or_404(Property, id=property_id)
    user_profile = request.user.profile

    # Retrieve the coupon code from the form
    coupon_code = request.POST.get('coupon_code')
    coupon = None
    discount = 0

    # Validate the coupon
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code, active=True)
            discount = coupon.discount_amount
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")
        else:
            messages.success(request, f"Coupon applied! You get a discount of {discount}.")

    # Calculate the final price after applying the coupon
    final_price = property_item.price - discount
    if final_price < 0:
        final_price = 0

    # Add the property to the cart with the final price
    cart, created = Cart.objects.get_or_create(user=user_profile)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, property=property_item, defaults={'quantity': 1})

    # Update the cart item's final price (you may need a separate field to store this in the cart model)
    cart_item.final_price = final_price
    cart_item.save()

    messages.success(request, f"Property {property_item.title} added to cart with a final price of {final_price}.")

    # Redirect to the cart view to show the updated cart
    return redirect('cart')


@login_required
def update_quantity(request, property_id):
    profile = Profile.objects.get(user=request.user)
    cart = get_object_or_404(Cart, user=profile)
    cart_item = get_object_or_404(CartItem, cart=cart, property_id=property_id)

    if 'increase' in request.POST:
        cart_item.quantity += 1
    elif 'decrease' in request.POST and cart_item.quantity > 1:
        cart_item.quantity -= 1

    cart_item.save()
    return redirect('cart')

@login_required
def purchase_property(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    profile = Profile.objects.get(user=request.user)
    cart = get_object_or_404(Cart, user=profile)
    cart_item = get_object_or_404(CartItem, cart=cart, property=property)

    if request.method == 'POST':
        # Handle coupon application
        coupon_code = request.POST.get('coupons')
        discount_amount = 0
        final_price = property.price

        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, active=True)
                discount_amount = coupon.discount_amount
                final_price -= discount_amount
                coupon.active = False
                coupon.save()
                messages.success(request, f'Coupon applied! Discount: {discount_amount}')
            except Coupon.DoesNotExist:
                messages.error(request, 'Invalid or inactive coupon')

        # Handle purchase
        if 'purchase' in request.POST:
            Sale.objects.create(
                property=property,
                employee=property.owner,
                buyer=request.user,
                sale_date=datetime.today().strftime('%Y-%m-%d'),
                contract_date=datetime.today().strftime('%Y-%m-%d'),
                sale_price=final_price
            )
            cart_item.delete()
            messages.success(request, f'Purchase successful for {property.title}!')
            return redirect('cart')  # Stay on cart page after purchase

    # Fetch active coupons
    active_coupons = Coupon.objects.filter(active=True)
    context = {
        'property': property,
        'active_coupons': active_coupons,
    }
    return render(request, 'property_detail.html', context)

@login_required
def apply_coupon(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            coupon_code = data.get('coupon')
            coupon = Coupon.objects.get(code=coupon_code, active=True)
            discount_amount = coupon.discount_amount
            final_price = calculate_final_price(discount_amount)  # Replace with your calculation logic
            coupon.active = False
            coupon.save()
            return JsonResponse({'success': True, 'message': f'Coupon applied! Discount: {discount_amount}', 'final_price': final_price})
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid or inactive coupon'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def home(request):
    latest_article = Article.objects.first()
    user_info = get_user_time()
    properties_list = Property.objects.all()
    sponsors = Sponsor.objects.all()

    sort_price = request.GET.get('sort_price', 'none')
    sort_area = request.GET.get('sort_area', 'none')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    min_area = request.GET.get('min_area')
    max_area = request.GET.get('max_area')
    title = request.GET.get('title')

    api_quote = 'No quote for not authorised!'
    if request.user.is_authenticated:
        api_url = 'https://favqs.com/api/qotd'
        response = requests.get(api_url)
        if response.status_code == 200:
            api_quote = response.json().get('quote', {}).get('body', api_quote)
        else:
            logger.error("Failed to retrieve quote from API")

    # Фильтрация по цене и площади
    if min_price:
        properties_list = properties_list.filter(price__gte=min_price)
    if max_price:
        properties_list = properties_list.filter(price__lte=max_price)
    if min_area:
        properties_list = properties_list.filter(square_meters__gte=min_area)
    if max_area:
        properties_list = properties_list.filter(square_meters__lte=max_area)
    if title:
        properties_list = properties_list.filter(title__icontains=title)

    # Сортировка по цене
    if sort_price != 'none':
        properties_list = properties_list.order_by(
            'price' if sort_price == 'ascending_price' else '-price'
        )
    
    # Сортировка по площади
    if sort_area != 'none':
        properties_list = properties_list.order_by(
            'square_meters' if sort_area == 'ascending_area' else '-square_meters'
        )

    # Пагинация: 3 элемента на страницу
    paginator = Paginator(properties_list, 3)  # 3 свойства на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Определение, является ли пользователь администратором
    is_admin = request.user.is_staff or request.user.is_superuser

    context = {
        'latest_article': latest_article,
        'username': request.user.username if request.user.is_authenticated else None,
        'user_timezone': user_info.get('user_timezone', 'UTC'),
        'current_date_formatted': user_info.get('current_date_formatted', datetime.now().strftime('%Y-%m-%d')),
        'calendar_text': user_info.get('calendar_text', ''),
        'page_obj': page_obj,
        'properties': page_obj.object_list,
        'quote': api_quote,
        'sponsors': sponsors,
        'is_admin': is_admin,
    }

    logger.info("Home page accessed")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        properties_html = render_to_string('partials/_property_list.html', context, request=request)
        return JsonResponse({'properties_html': properties_html})

    return render(request, 'home.html', context)

def client_list_view(request):
    clients = User.objects.all().order_by('last_name')
    total_sales = Sale.objects.aggregate(
        total_sales=Sum('sale_price'))['total_sales']
    return render(request, 'stats/client_list.html', {'clients': clients, 'total_sales': total_sales})

@login_required
def remove_from_cart(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)
    profile = Profile.objects.get(user=request.user)  # Ensure Profile instance is used
    cart = get_object_or_404(Cart, user=profile)

    # Find the cart item associated with the cart and property
    cart_item = get_object_or_404(CartItem, cart=cart, property=property_obj)
    cart_item.delete()

    messages.success(request, f'{property_obj.title} has been removed from your cart.')
    return redirect('cart')


def sales_statistics_view(request):
    sales = Sale.objects.all()
    avg_sales = sales.aggregate(Avg('sale_price'))['sale_price__avg']

    sales_count = sales.count()
    sorted_sales = sales.order_by('sale_price')
    median_sales = sorted_sales[sales_count // 2].sale_price if sales_count % 2 != 0 else \
        (sorted_sales[sales_count // 2 - 1].sale_price +
         sorted_sales[sales_count // 2].sale_price) / 2
    mode_sales = sales.values('sale_price').annotate(
        count=Count('sale_price')).order_by('-count').first()['sale_price']

    return render(request, 'stats/sales_statistics.html', {
        'avg_sales': avg_sales,
        'median_sales': median_sales,
        'mode_sales': mode_sales
    })


def is_admin(user):
    logger.info("Admin accessed property list")
    return user.is_superuser

@user_passes_test(is_admin)
def property_list(request):
    properties = Property.objects.all()
    return render(request, 'property_list.html', {'properties': properties})


@user_passes_test(is_admin)
def property_create(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            logger.info("Property created successfully")
            messages.success(request, 'Property has been added successfully.')
            return redirect('property_list')
    else:
        form = PropertyForm()
    return render(request, 'property_form.html', {'form': form, 'title': 'Add Property'})


@user_passes_test(is_admin)
def property_update(request, pk):
    property = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property)
        if form.is_valid():
            form.save()
            logger.info(f"Property {property.id} updated successfully")
            messages.success(
                request, 'Property has been updated successfully.')
            return redirect('property_list')
    else:
        form = PropertyForm(instance=property)
    return render(request, 'property_form.html', {'form': form, 'title': 'Edit Property'})


@user_passes_test(is_admin)
def property_delete(request, pk):
    property = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        property.delete()
        logger.info(f"Property {property.id} deleted successfully")
        messages.success(request, 'Property has been deleted successfully.')
        return redirect('property_list')
    return render(request, 'property_confirm_delete.html', {'property': property})


@user_passes_test(is_admin)
def contact_list(request):
    contacts = Contact.objects.all()
    return render(request, 'contact_list.html', {'contacts': contacts})


@user_passes_test(is_admin)
def contact_create(request):
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact has been added successfully.')
            return redirect('contact_list')
    else:
        form = ContactForm()
    return render(request, 'contact_form.html', {'form': form, 'title': 'Add Contact'})


@user_passes_test(is_admin)
def contact_update(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact has been updated successfully.')
            return redirect('contact_list')
    else:
        form = ContactForm(instance=contact)
    return render(request, 'contact_form.html', {'form': form, 'title': 'Edit Contact'})


@user_passes_test(is_admin)
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Contact has been deleted successfully.')
        return redirect('contact_list')
    return render(request, 'contact_confirm_delete.html', {'contact': contact})


@login_required
def profile(request):
    user = request.user
    username = user.username
    role = "admin" if user.is_superuser else "user"

    nationality_api_url = f'https://api.nationalize.io/?name={username}'
    nationality_response = requests.get(nationality_api_url)
    if nationality_response.status_code == 200:
        nationality_data = nationality_response.json()
        if nationality_data['country']:
            nationalities = ', '.join(
                [f"{country['country_id']} ({country['probability']*100:.2f}%)" for country in nationality_data['country']])
        else:
            nationalities = "No nationalities found."
    else:
        nationalities = "Unable to determine nationality."

    context = {
        'full_name': username,
        'role': role,
        'nationalities': nationalities,
        'email': user.email,
        'joined': user.date_joined
    }

    return render(request, 'profile.html', context)


def statistics(request):
    clients = User.objects.order_by('username').values('username', 'email')
    properties = Property.objects.order_by('title')

    total_sales = Sale.objects.aggregate(Sum('sale_price'))['sale_price__sum']
    avg_sales = Sale.objects.aggregate(Avg('sale_price'))['sale_price__avg']
    max_sales = Sale.objects.aggregate(Max('sale_price'))['sale_price__max']

    popular_category = Property.objects.values('property_types__name').annotate(
        count=Count('id')).order_by('-count').first()

    category_counts = Property.objects.values('property_types__name').annotate(
        count=Count('id')).order_by('-count')

    profitable_property = Sale.objects.values('property__title').annotate(
        total_profit=Sum('sale_price')
    ).order_by('-total_profit').first()

    total_clients = User.objects.count()
    client_purchase_counts = Sale.objects.values('buyer__username').annotate(
        purchase_count=Count('id')).order_by('-purchase_count')

    context = {
        'clients': clients,
        'properties': properties,
        'total_sales': total_sales,
        'avg_sales': avg_sales,
        'max_sales': max_sales,
        'popular_category': popular_category,
        'most_profitable_property': profitable_property,
        'category_counts': list(category_counts),
        'total_clients': total_clients,
        'client_purchase_counts': client_purchase_counts,
    }
    return render(request, 'statistics.html', context)


def client_age_statistics_view(request):
    clients = User.objects.annotate(age=Max('date_joined'))
    avg_age = clients.aggregate(Avg('age'))['age__avg']
    median_age = clients.order_by('age')[clients.count() // 2].age

    return render(request, 'stats/client_age_statistics.html', {
        'avg_age': avg_age,
        'median_age': median_age
    })


def popular_properties_view(request):
    popular_properties = Property.objects.annotate(
        sale_count=Count('sales')).order_by('-sale_count')
    most_profitable_properties = Property.objects.annotate(
        total_revenue=Sum('sales__sale_price')).order_by('-total_revenue')

    logger.info("Popular properties page accessed")
    return render(request, 'stats/popular_properties.html', {
        'popular_properties': popular_properties,
        'most_profitable_properties': most_profitable_properties
    })


def property_detail(request, property_id):
    property = get_object_or_404(Property, pk=property_id)
    active_coupons = Coupon.objects.filter(active=True)
    context = {
        'property': property,
        'active_coupons': active_coupons,
    }
    return render(request, 'property_detail.html', context)

def about(request):
    company_info = CompanyInfo.objects.first()
    context = {
        'company_info': company_info,
    }
    return render(request, 'about.html', context)


def news(request):
    articles = Article.objects.all()
    context = {
        'articles': articles,
    }
    return render(request, 'news.html', context)

def dictionary(request):
    terms = Dictionary.objects.all()
    context = {
        'terms': terms,
    }
    return render(request, 'dictionary.html', context)


def contacts(request):
    return render(request, 'contacts.html')


def privacy_policy(request):
    return render(request, 'privacy_policy.html')


def vacancies(request):
    vacancies = Vacancy.objects.all()
    context = {
        'vacancies': vacancies,
    }
    return render(request, 'vacancies.html', context)


def coupons(request):
    all_coupons = Coupon.objects.all()
    for coupon in all_coupons:
        print(f"Coupon: {coupon.code}, Active: {coupon.active}")
    
    active_coupons = Coupon.objects.filter(active=True)
    print(active_coupons)  # Print the active coupons queryset
    return render(request, 'coupons.html', {'active_coupons': active_coupons})

def article_detail(request, article_id):
    article = Article.objects.get(id=article_id)
    context = {
        'article': article,
    }
    return render(request, 'article_detail.html', context)
