from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import UserProfile
from adminpanel.models import Product, Category, Notification, Order, OrderItem
from .models import Cart, Wishlist
import re


# ===================== HOME =====================

def home(request):
    return render(request, "app/index.html")


# ===================== SHOP =====================

def shop(request):
    category_name = request.GET.get("category")
    search = request.GET.get("search")

    products = Product.objects.all()
    categories = Category.objects.all()

    if category_name:
        products = products.filter(category__name__iexact=category_name)

    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(brand__icontains=search)
        )

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list("product_id", flat=True)

    context = {
        "products": products,
        "categories": categories,
        "wishlist_ids": wishlist_ids
    }

    return render(request, "app/shop.html", context)


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


# ===================== CART =====================

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

    Wishlist.objects.filter(user=request.user, product=product).delete()

    if request.headers.get("x-requested-with") != "XMLHttpRequest":
        messages.success(request, f"{product.name} added to cart")
        return redirect("shop")

    count = Cart.objects.filter(user=request.user).count()
    return JsonResponse({"success": True, "cart_count": count})


@login_required
def cart_view(request):
    items = Cart.objects.filter(user=request.user)

    original_total = sum(item.product.price * item.quantity for item in items)
    discounted_total = sum(item.product.get_final_price() * item.quantity for item in items)

    discount_total = original_total - discounted_total
    delivery_charge = 0 if discounted_total >= 999 else 50
    grand_total = discounted_total + delivery_charge

    context = {
        "items": items,
        "original_total": round(original_total, 0),
        "discount_total": round(discount_total, 0),
        "delivery_charge": delivery_charge,
        "grand_total": round(grand_total, 0),
        "total": round(discounted_total, 0),
        "total_saved": round(discount_total, 0),
    }

    return render(request, "app/cart.html", context)


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
    get_object_or_404(Cart, id=item_id, user=request.user).delete()
    return redirect("cart")


# ===================== WISHLIST =====================

@login_required
def toggle_wishlist(request, product_id):
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
    products = Product.objects.filter(wishlist__user=request.user)
    wishlist_ids = products.values_list("id", flat=True)

    return render(request, "app/wishlist.html", {
        "products": products,
        "wishlist_ids": wishlist_ids,
    })


@login_required
def remove_from_wishlist(request, item_id):
    get_object_or_404(Wishlist, id=item_id, user=request.user).delete()
    return redirect("wishlist")


# ===================== AUTH =====================

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

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully!")
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

    return render(request, "app/login.html")


def logout_view(request):
    logout(request)
    return redirect("home")


# ===================== CHECKOUT =====================

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect("cart")

    if request.method == "POST":
        total_amount = Decimal("0.00")

        order = Order.objects.create(
            user=request.user,
            full_name=request.POST["full_name"],
            phone=request.POST["phone"],
            address=request.POST["address"],
            city=request.POST["city"],
            state=request.POST["state"],
            pincode=request.POST["pincode"],
            payment_method=request.POST["payment"],
            total_amount=0,
        )

        for item in cart_items:
            price = item.product.get_final_price()
            line_total = price * item.quantity
            total_amount += line_total

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=price
            )

            item.product.stock -= item.quantity
            item.product.save()

        order.total_amount = total_amount
        order.save()

        cart_items.delete()

        return redirect("order_success")

    subtotal = sum(
        item.product.get_final_price() * item.quantity
        for item in cart_items
    )

    delivery = 0 if subtotal >= 999 else 50
    total = subtotal + delivery

    return render(request, "app/checkout.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "delivery": delivery,
        "total": total,
    })


# ===================== ORDERS =====================

@login_required
def order_history(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(request, "app/order_history.html", {
        "orders": orders
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    items = order.items.all()

    return render(request, "app/order_detail.html", {
        "order": order,
        "items": items
    })


@login_required
def order_success(request):
    return render(request, "app/order_success.html")


# ===================== STATIC PAGES =====================

def about(request):
    return render(request, "app/about.html")


def contact(request):
    return render(request, "app/contact.html")


# ===================== NOTIFICATIONS =====================

@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(
        receiver=request.user,
        is_read=False
    ).order_by("-id")

    data = [
        {
            "id": n.id,
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
        receiver=request.user
    )

    notification.is_read = True
    notification.save()

    return JsonResponse({"success": True})

def virtual_try(request):
    return render(request, 'virtual_try.html')

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, "app/profile.html", {"profile": profile})

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        phone = request.POST.get("phone", "").strip()

        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Phone number must be exactly 10 digits.")
            return render(request, "app/edit_profile.html", {"profile": profile})

        # Save data
        request.user.first_name = request.POST.get("first_name").capitalize()
        request.user.last_name = request.POST.get("last_name").capitalize()
        request.user.email = request.POST.get("email")
        profile.phone = phone

        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES.get("profile_image")

        request.user.save()
        profile.save()

      

        # IMPORTANT → redirect nai karvu
        return render(request, "app/edit_profile.html", {
            "profile": profile,
            "redirect": True
        })

    return render(request, "app/edit_profile.html", {"profile": profile})

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("profile")
    else:
       form = PasswordChangeForm(request.user, request.POST)
    for field in form.fields.values():
     field.widget.attrs.update({
        "placeholder": " ",
        "class": "form-input"
    })
    return render(request, "app/change_password.html", {"form": form})

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')

        if User.objects.filter(email=email).exists():
            messages.success(request, "Password reset link sent to your email.")
        else:
            messages.error(request, "Email not registered.")

    return render(request, "app/forgot_password.html")