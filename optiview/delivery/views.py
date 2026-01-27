from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
#from .models import DeliveryPerson
from adminpanel.models import Order
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings


@login_required
def delivery_dashboard(request):
    # Safety check (extra protection)
    if not hasattr(request.user, "deliveryperson"):
        return redirect("delivery_login")

    assigned_orders = (
        Order.objects
        .select_related("delivery_person")
        .filter(delivery_person=request.user.deliveryperson)
    )

    return render(request, "delivery/dashboard.html", {
        "orders": assigned_orders
    })


def delivery_logout(request):
    logout(request)
    return redirect('delivery_login')


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_link = request.build_absolute_uri(
                f"/reset-password/{uid}/{token}/"
            )

            send_mail(
                "Password Reset",
                f"Click link to reset password:\n{reset_link}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

        return render(request, "delivery/forgot_password.html",
                      {"msg": "If email exists, reset link sent"})

    return render(request, "delivery/forgot_password.html")

def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password = request.POST.get("password")
            user.set_password(password)
            user.save()
            return redirect("login")

        return render(request, "delivery/reset_password.html")

    return render(request, "delivery/reset_password.html",
                  {"error": "Invalid or expired link"})

def delivery_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            return render(request, "delivery/login.html", {
                "error": "Both fields are required"
            })

        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request, "delivery/login.html", {
                "error": "Invalid username or password"
            })

        if not hasattr(user, "deliveryperson"):
            return render(request, "delivery/login.html", {
                "error": "You are not authorized as delivery person"
            })

        login(request, user)
        return redirect("delivery_dashboard")

    return render(request, "delivery/login.html")



