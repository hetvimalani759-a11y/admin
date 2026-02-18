from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from functools import wraps
from adminpanel.utils import is_delivery

from adminpanel.models import Order
from .models import DeliveryPerson


# =====================================================
# 🔐 DELIVERY ACCESS GUARD
# =====================================================
def delivery_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("delivery:delivery_login")

        if request.session.get("panel") != "delivery":
            logout(request)
            request.session.flush()
            return redirect("delivery:delivery_login")

        if not hasattr(request.user, "deliveryperson"):
            logout(request)
            request.session.flush()
            return redirect("delivery:delivery_login")

        return view_func(request, *args, **kwargs)
    return wrapper


# =====================================================
# 🚪 LOGOUT
# =====================================================
@delivery_required
def delivery_logout(request):
    logout(request)
    request.session.flush()
    return redirect("delivery:delivery_login")


# =====================================================
# 🔑 FORGOT PASSWORD
# =====================================================
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(
                f"/delivery/reset-password/{uid}/{token}/"
            )

            send_mail(
                "Password Reset",
                f"Click link to reset password:\n{reset_link}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

        return render(request, "delivery/forgot_password.html", {
            "msg": "If the email exists, a reset link has been sent."
        })

    return render(request, "delivery/forgot_password.html")


# =====================================================
# 🔑 RESET PASSWORD
# =====================================================
def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if not user or not default_token_generator.check_token(user, token):
        return render(request, "delivery/reset_password.html", {
            "error": "Invalid or expired reset link."
        })

    if request.method == "POST":
        password = request.POST.get("password")
        user.set_password(password)
        user.save()
        messages.success(request, "Password reset successful. Please login.")
        return redirect("delivery:delivery_login")

    return render(request, "delivery/reset_password.html")


# =====================================================
# 🔐 LOGIN
# =====================================================
def delivery_login(request):
    if request.user.is_authenticated and is_delivery(request.user):
        return redirect("app:home")
    request.session.flush()

    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )

        if not user or not hasattr(user, "deliveryperson"):
            messages.error(request, "Delivery account required")
            return redirect("delivery:delivery_login")

        login(request, user)
        request.session["panel"] = "delivery"
        return redirect("delivery:delivery_dashboard")

    return render(request, "delivery/login.html")


# =====================================================
# 📊 DASHBOARD
# =====================================================
@login_required(login_url="delivery:delivery_login")
@delivery_required
def delivery_dashboard(request):
    delivery_person = request.user.deliveryperson
    orders = Order.objects.filter(delivery_person=delivery_person)

    context = {
        "total_orders": orders.count(),
        "pending_orders": orders.filter(status="Pending").count(),
        "out_for_delivery": orders.filter(status="Out for Delivery").count(),
        "delivered_orders": orders.filter(status="Delivered").count(),
        "active_orders": orders.filter(status__in=["Placed", "Out for Delivery"]),
    }

    return render(request, "delivery/dashboard.html", context)


# =====================================================
# 📦 MY ORDERS
# =====================================================
@login_required(login_url="delivery:delivery_login")
@delivery_required
def my_orders(request):
    orders = Order.objects.filter(delivery_person=request.user.deliveryperson)
    return render(request, "delivery/my_orders.html", {"orders": orders})


# =====================================================
# 👤 PROFILE
# =====================================================
@login_required(login_url="delivery:delivery_login")
@delivery_required
def delivery_profile(request):
    return render(request, "delivery/profile.html", {
        "delivery_person": request.user.deliveryperson
    })


# =====================================================
# ✏️ EDIT PROFILE
# =====================================================
@login_required(login_url="delivery:delivery_login")
@delivery_required
def edit_profile(request):
    user = request.user
    delivery_person = user.deliveryperson

    if request.method == "POST":
        user.username = request.POST.get("username", "").strip()
        user.email = request.POST.get("email")

        password = request.POST.get("password")
        if password:
            user.set_password(password)

        user.save()

        delivery_person.phone = request.POST.get("phone")
        delivery_person.address = request.POST.get("address")
        delivery_person.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("delivery:delivery_profile")

    return render(request, "delivery/edit_profile.html", {
        "user": user,
        "delivery_person": delivery_person
    })


# =====================================================
# ❌ REMOVE ADMIN LOGIC FROM DELIVERY APP
# (Delivery creation should stay in adminpanel)
# =====================================================
