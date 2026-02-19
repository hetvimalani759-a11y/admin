from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from decimal import Decimal

from adminpanel.models import Product, Category, Notification, Order, OrderItem
from .models import Cart, Wishlist


# ==========================================================
# HOME
# ==========================================================

def home(request):
    return render(request, "app/index.html")


# ==========================================================
# SHOP
# ==========================================================

def shop(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    category_name = request.GET.get("category")
    selected_shapes = request.GET.getlist("shape")
    selected_colors = request.GET.getlist("color")
    selected_sizes = request.GET.getlist("size")
    selected_price = request.GET.get("price")

    if category_name:
        products = products.filter(category__name__iexact=category_name)

    if selected_shapes:
        products = products.filter(frame_shape__in=selected_shapes)

    if selected_colors:
        products = products.filter(frame_color__in=selected_colors)

    if selected_sizes:
        products = products.filter(frame_size__in=selected_sizes)

    if selected_price:
        if selected_price == "under_1000":
            products = products.filter(price__lt=1000)
        elif selected_price == "1000_2000":
            products = products.filter(price__gte=1000, price__lte=2000)
        elif selected_price == "above_2000":
            products = products.filter(price__gt=2000)

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list("product_id", flat=True)

    return render(request, "app/shop.html", {
        "products": products,
        "categories": categories,
        "wishlist_ids": wishlist_ids,
        "selected_shapes": selected_shapes,
        "selected_colors": selected_colors,
        "selected_sizes": selected_sizes,
        "selected_price": selected_price,
    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list("product_id", flat=True)

    return render(request, "app/product_detail.html", {
        "product": product,
        "wishlist_ids": wishlist_ids
    })


# ==========================================================
# CART
# ==========================================================

@login_required
def add_to_cart(request, product_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    count = Cart.objects.filter(user=request.user).count()

    return JsonResponse({
        "success": True,
        "cart_count": count
    })


@login_required
def cart_view(request):
    items = Cart.objects.filter(user=request.user)

    original_total = 0
    total = 0

    for item in items:
        original_total += item.product.price * item.quantity
        total += item.product.get_final_price() * item.quantity

    discount_total = original_total - total
    delivery_charge = 0 if total >= 999 else 50
    grand_total = total + delivery_charge
    total_saved = original_total - total

    return render(request, 'app/cart.html', {
        'items': items,
        'original_total': round(original_total, 0),
        'discount_total': round(discount_total, 0),
        'delivery_charge': delivery_charge,
        'grand_total': round(grand_total, 0),
        'total': round(total, 0),
        'total_saved': round(total_saved, 0),
    })


@login_required
def cart_count(request):
    return JsonResponse({
        "count": Cart.objects.filter(user=request.user).count()
    })


@login_required
def increase_qty(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)
    item.quantity += 1
    item.save()
    return redirect("cart")


@login_required
def decrease_qty(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect("cart")


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)
    item.delete()
    return redirect("cart")


# ==========================================================
# WISHLIST
# ==========================================================

@login_required
def toggle_wishlist(request, product_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    product = get_object_or_404(Product, id=product_id)

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        wishlist_item.delete()
        return JsonResponse({"status": "removed"})

    return JsonResponse({"status": "added"})


@login_required
def wishlist_view(request):
    products = Product.objects.filter(
        wishlist__user=request.user
    ).distinct()

    return render(request, 'app/wishlist.html', {
        'products': products,
    })


@login_required
def remove_from_wishlist(request, item_id):
    item = get_object_or_404(Wishlist, id=item_id, user=request.user)
    item.delete()
    return redirect("wishlist")



# ==========================================================
# AUTH
# ==========================================================

def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Passwords do not match!")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("register")

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")

    return render(request, "app/register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("home")

        messages.error(request, "Invalid username or password!")
        return redirect("login")

    return render(request, "app/login.html")


def logout_view(request):
    logout(request)
    return redirect("home")


# ==========================================================
# STATIC PAGES
# ==========================================================

def about(request):
    return render(request, "app/about.html")


def contact(request):
    return render(request, "app/contact.html")


# ==========================================================
# NOTIFICATIONS
# ==========================================================

@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by("-created_at")

    data = [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message
        }
        for n in notifications
    ]

    return JsonResponse({"notifications": data})


@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(
        Notification,
        id=pk,
        user=request.user
    )
    notification.is_read = True
    notification.save()

    return JsonResponse({"success": True})


# ==========================================================
# CHECKOUT & ORDERS
# ==========================================================

@login_required
def checkout(request):
    items = Cart.objects.filter(user=request.user)

    if not items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect("cart")

    total = sum(item.product.get_final_price() * item.quantity for item in items)
    delivery_charge = 0 if total >= 999 else 50
    grand_total = total + delivery_charge

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user,
            total_price=grand_total
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.get_final_price()
            )

        items.delete()
        messages.success(request, "Order placed successfully!")
        return redirect("home")

    return render(request, "app/checkout.html", {
        "items": items,
        "total": round(total, 0),
        "delivery_charge": delivery_charge,
        "grand_total": round(grand_total, 0),
    })


@login_required
def order_success(request):
    return render(request, "app/order_success.html")


@login_required
def place_order(request):
    return redirect("checkout")


@login_required
def order_history(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by("-id")

    return render(request, "app/order_history.html", {
        "orders": orders
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "app/order_detail.html", {'order': order})
