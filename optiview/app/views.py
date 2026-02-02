from itertools import product
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from adminpanel.models import Product, Category, Notification,Order,OrderItem
from .models import Cart, Wishlist


# -------------------- HOME --------------------
def home(request):
    return render(request, "app/index.html")


# -------------------- SHOP --------------------
def shop(request):
    category_name = request.GET.get("category")
    categories = Category.objects.all()
    products = Product.objects.all()

    if category_name:
        products = products.filter(category__name__iexact=category_name)

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(user=request.user).values_list("product_id", flat=True)

    return render(request, "app/shop.html", {
        "products": products,
        "categories": categories,
        "wishlist_ids": wishlist_ids
    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(user=request.user).values_list("product_id", flat=True)

    return render(request, "app/product_detail.html", {"product": product, "wishlist_ids": wishlist_ids})


# -------------------- CART --------------------


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={"quantity": 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Remove from wishlist if present
    Wishlist.objects.filter(user=request.user, product=product).delete()

    # Full-page message for non-AJAX
    if request.headers.get("x-requested-with") != "XMLHttpRequest":
        messages.success(request, f"{product.name} added to cart")
        return redirect("shop")

    # AJAX response
    count = Cart.objects.filter(user=request.user).count()
    return JsonResponse({"success": True, "cart_count": count})



@login_required
def cart_view(request):
    items = Cart.objects.filter(user=request.user )

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
    return JsonResponse({"count": Cart.objects.filter(user=request.user).count()})


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
    get_object_or_404(Cart, id=item_id, user=request.user).delete()
    return redirect("cart")


# -------------------- WISHLIST --------------------
@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if not created:
        wishlist_item.delete()
        return JsonResponse({"status": "removed"})
    return JsonResponse({"status": "added"})


@login_required
def wishlist_view(request):
    products = Product.objects.filter(wishlist__user=request.user)
    wishlist_ids = products.values_list('id', flat=True)

    return render(request, 'app/wishlist.html', {
        'products': products,
        'wishlist_ids': wishlist_ids,
    })
@login_required
def remove_from_wishlist(request, item_id):
    get_object_or_404(Wishlist, id=item_id, user=request.user).delete()
    return redirect("wishlist")


# -------------------- AUTH --------------------
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


# -------------------- STATIC PAGES --------------------
def about(request):
    return render(request, "app/about.html")


def contact(request):
    return render(request, "app/contact.html")


# -------------------- 🔔 NOTIFICATIONS --------------------
@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by("-created_at")
    data = [{"id": n.id, "title": n.title, "message": n.message} for n in notifications]
    return JsonResponse({"notifications": data})


@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, id=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({"success": True})






# user_app/views.py
# user_app/views.py
from django.shortcuts import render, redirect
from .models import CartItem


from django.contrib.auth.decorators import login_required
from decimal import Decimal

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)

    if request.method == "POST":
        total_amount = Decimal("0.00")

        order = Order.objects.create(
            user=request.user,
            full_name=request.POST['full_name'],
            phone=request.POST['phone'],
            address=request.POST['address'],
            city=request.POST['city'],
            state=request.POST['state'],
            pincode=request.POST['pincode'],
            payment_method=request.POST['payment'],
            total_amount=0,
        )

        for item in cart_items:
            product = item.product
            price = product.get_final_price()   # ✅ OFFER PRICE USED HERE
            line_total = price * item.quantity
            total_amount += line_total

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=price  # ✅ stored discounted price
            )

            # Update stock
            product.stock -= item.quantity
            product.save()

        order.total_amount = total_amount
        order.save()

        cart_items.delete()
        return redirect("order_success")

    # -------- GET REQUEST --------
    subtotal = sum(item.product.get_final_price() * item.quantity for item in cart_items)
    delivery = 0 if subtotal >= 999 else 50
    total = subtotal + delivery
    saved_amount = sum(
        (item.product.price - item.product.get_final_price()) * item.quantity
        for item in cart_items
        if item.product.get_offer()
    )

    has_address = request.session.get("saved_address", False)

    return render(request, "app/checkout.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "delivery": delivery,
        "total": total,
        "saved_amount": saved_amount,
        "has_address": has_address,
    })


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'app/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all()  # Related name from OrderItem
    return render(request, 'app/order_detail.html', {
        'order': order,
        'items': items
    })
@login_required
def order_success(request):
    return render(request, "app/order_success.html")


def place_order(request):
    if request.method == "POST":
        product = request.POST.get("product")
        quantity = int(request.POST.get("quantity"))
        price = float(request.POST.get("price"))

        Order.objects.create(
            user=request.user,
            product_name=product,
            quantity=quantity,
            price=price
        )

        return redirect("order_success")

    return render(request, "app/place_order.html")