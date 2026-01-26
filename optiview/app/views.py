from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from adminpanel.models import Product, Lens, Order, Category
from .models import Cart, Wishlist, Notification

# -------------------- HOME --------------------

def home(request):
    return render(request, "app/index.html")


# -------------------- SHOP --------------------

# def shop(request):
#     products = Product.objects.all()
#     categories = Category.objects.all()

#     search_query = request.GET.get('search')
#     category_filter = request.GET.get('category')

#     if search_query:
#         products = products.filter(name__icontains=search_query)

#     if category_filter:
#         products = products.filter(category__name=category_filter)

#     context = {
#         'products': products,
#         'categories': categories
#     }

#     return render(request, 'app/shop.html', context)
def shop(request):
    products = Product.objects.all()
    wishlist_ids = []

    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)

    return render(request, 'app/shop.html', {
        'products': products,
        'wishlist_ids': wishlist_ids
    })


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )
    if not created:
        item.quantity += 1
        item.save()

    return redirect('cart')


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('shop')


# -------------------- PRODUCT --------------------

def product_list(request):
    products = Product.objects.all()
    return render(request, 'app/product_list.html', {'products': products})


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'app/product_detail.html', {'product': product})


# -------------------- AUTH --------------------

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register')

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')

    return render(request, "app/register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password!")
            return redirect('login')

    return render(request, "app/login.html")


def logout_view(request):
    user = request.user
    logout(request)
    user.is_active = False
    user.save()
    return redirect("home")


# -------------------- STATIC PAGES --------------------

def about(request):
    return render(request, 'app/about.html')


def contact(request):
    return render(request, 'app/contact.html')


# -------------------- NOTIFICATIONS --------------------

def notifications(request):
    data = Notification.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "app/notifications.html", {"notifications": data})


def mark_read(request, id):
    Notification.objects.filter(id=id, user=request.user).update(is_read=True)
    return redirect("notifications")

@login_required
def cart_view(request):
    items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in items)

    return render(request, 'app/cart.html', {
        'items': items,   # ✅ template match
        'total': total
    })
@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)
    item.delete()
    return redirect('cart')
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )
    if not created:
        item.quantity += 1
        item.save()

    return redirect('cart')   # ✅ DIRECT CART

@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    return render(request, 'app/wishlist.html', {
        'wishlist': wishlist   # ✅ template match
    })
@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    return redirect('shop')
@login_required
def increase_qty(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)
    item.quantity += 1
    item.save()
    return redirect('cart')


@login_required
def decrease_qty(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()   # qty 1 હોય તો remove

    return redirect('cart')


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('shop')


@login_required
def remove_from_wishlist(request, item_id):
    item = get_object_or_404(Wishlist, id=item_id, user=request.user)
    item.delete()
    return redirect('wishlist')
