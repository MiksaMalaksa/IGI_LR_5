from datetime import date, datetime
from django.forms import ValidationError
from django.http import JsonResponse
from .models import Contact
from .forms import ContactForm, ReviewForm, PropertyForm
import logging
import requests
from agency.models import Property, Sale, Cart, CartItem, User, Profile
from django.db.models import Avg, Max, Count, Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .utils import get_user_time
from company.models import Article, CompanyInfo, Dictionary, Vacancy, Review, Coupon

logger = logging.getLogger(__name__)

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

@login_required
def add_to_cart(request, property_id):
    # Get the property object
    property_obj = get_object_or_404(Property, id=property_id)

    # Ensure a Profile exists for the user, create if not
    profile, created = Profile.objects.get_or_create(user=request.user)

    # Get or create the cart associated with the user's profile
    cart, created = Cart.objects.get_or_create(user=profile)  # Ensure Profile instance is used

    # Get or create the cart item
    cart_item, created = CartItem.objects.get_or_create(cart=cart, property=property_obj)

    # If the item already exists, increment the quantity
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Add a success message
    messages.success(request, f'{property_obj.title} has been added to your cart.')
    return redirect('cart')

@login_required
def cart_view(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={'birthdate': date.today()}  # Use a default birthdate, such as today's date
    )
    cart, created = Cart.objects.get_or_create(user=profile)
    cart_items = CartItem.objects.filter(cart=cart)

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
            elif f'purchase_{item.property.id}' in request.POST:
                purchase_property(request, item.property.id)
                item.delete()

        return redirect('cart')

    total_price = sum(item.property.price * item.quantity for item in cart_items)
    context = {'cart_items': cart_items, 'total_price': total_price}
    return render(request, 'cart.html', context)

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
    properties = Property.objects.all()

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

    if min_price:
        properties = properties.filter(price__gte=min_price)
    if max_price:
        properties = properties.filter(price__lte=max_price)
    if min_area:
        properties = properties.filter(square_meters__gte=min_area)
    if max_area:
        properties = properties.filter(square_meters__lte=max_area)
    if title:
        properties = properties.filter(title__icontains=title)

    if sort_price != 'none':
        properties = properties.order_by(
            'price' if sort_price == 'ascending_price' else '-price'
        )
    if sort_area != 'none':
        properties = properties.order_by(
            'square_meters' if sort_area == 'ascending_area' else '-square_meters'
        )

    context = {
        'latest_article': latest_article,
        'username': request.user.username if request.user.is_authenticated else None,
        'user_timezone': user_info['user_timezone'],
        'current_date_formatted': user_info['current_date_formatted'],
        'calendar_text': user_info['calendar_text'],
        'properties': properties,
        'quote': api_quote,
    }
    logger.info("Home page accessed")
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
    contacts = Contact.objects.all()
    context = {
        'contacts': contacts,
    }
    return render(request, 'contacts.html', context)


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
