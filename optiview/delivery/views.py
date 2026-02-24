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
from django.contrib.admin.views.decorators import staff_member_required
from .models import DeliveryPerson
from adminpanel.models import Order, Notification


# =========================
# DELIVERY LOGIN
# =========================
def delivery_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=username, password=password)

        if not user:
            messages.error(request, "Invalid username or password")
            return redirect("delivery:delivery_login")


        if not hasattr(user, "delivery_profile"):
            messages.error(request, "You are not a registered delivery person")
            return redirect("delivery:delivery_login")


        login(request, user)
        messages.success(request, "Login successful 🎉")
        return redirect("delivery:delivery_dashboard")

    return render(request, "delivery/login.html")


# =========================
# LOGOUT
# =========================
@login_required
def delivery_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully 👋")
    return redirect("delivery:delivery_login")



# =========================
# DASHBOARD
# =========================
@login_required
def delivery_dashboard(request):
    delivery_person = get_object_or_404(DeliveryPerson, user=request.user)
    orders = Order.objects.filter(delivery_person=delivery_person).order_by("-created_at")

    context = {
        "total_orders": orders.count(),
        "out_for_delivery": orders.filter(status="Out for Delivery").count(),
        "delivered_orders": orders.filter(status="Delivered").count(),
        "pending_orders": orders.filter(status="Placed").count(),
        "active_orders": orders.filter(status__in=["Placed", "Out for Delivery"]),
    }

    return render(request, "delivery/dashboard.html", context)


# =========================
# MY ORDERS
# =========================
@login_required
def my_orders(request):
    delivery_person = get_object_or_404(DeliveryPerson, user=request.user)
    orders = Order.objects.filter(delivery_person=delivery_person).order_by("-created_at")
    return render(request, "delivery/my_orders.html", {"orders": orders})

@login_required
def accept_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    order.status = "Out for Delivery"
    order.save()

    Notification.objects.create(
        sender=request.user,
        receiver=order.user,
        order=order,
        title="Order Accepted",
        message=f"Order #{order.id} is out for delivery."
    )

    return redirect("adminpanel:order_list")


@login_required
def reject_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    order.status = "Rejected"
    order.save()

    Notification.objects.create(
        sender=request.user,
        receiver=order.user,
        order=order,
        title="Order Rejected",
        message=f"Order #{order.id} has been rejected."
    )

    return redirect("adminpanel:order_list")




# =========================
# PROFILE
# =========================
@login_required
def delivery_profile(request):
    delivery_person = get_object_or_404(DeliveryPerson, user=request.user)
    return render(request, "delivery/profile.html", {"delivery_person": delivery_person})


# =========================
# EDIT PROFILE
# =========================
@login_required
def edit_profile(request):
    user = request.user
    delivery_person = get_object_or_404(DeliveryPerson, user=user)

    if request.method == "POST":
        user.username = request.POST.get("username", user.username)
        user.email = request.POST.get("email", user.email)
        user.save()

        phone = request.POST.get("phone", delivery_person.phone)

        if phone and (not phone.isdigit() or len(phone) != 10):
            return render(request, "delivery/edit_profile.html", {
                "user": user,
                "delivery_person": delivery_person,
                "error_message": "Enter valid 10 digit phone number"
            })

        delivery_person.phone = phone
        delivery_person.address = request.POST.get("address", delivery_person.address)

        if request.FILES.get("profile_image"):
            delivery_person.profile_image = request.FILES["profile_image"]

        delivery_person.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("delivery:edit_profile")

    return render(request, "delivery/edit_profile.html", {
        "user": user,
        "delivery_person": delivery_person
    })



@login_required
@staff_member_required
def assign_delivery(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        delivery_id = request.POST.get("delivery_person")
        delivery_person = get_object_or_404(DeliveryPerson, id=delivery_id)

        order.delivery_person = delivery_person
        order.status = "Assigned"
        order.save()

        # Notification create karo
        Notification.objects.create(
            user=delivery_person.user,
            title="New Order Assigned",
            message=f"Order #{order.id} tamne assign thayu che."
        )

        messages.success(request, "Delivery person assigned successfully.")
        return redirect("admin_orders")


# =========================
# DELIVERY ACTION
# =========================
@login_required
def delivery_action(request, order_id, action):
    order = get_object_or_404(Order, id=order_id)

    # 🔐 Security Check
    if not order.delivery_person or order.delivery_person.user != request.user:
        messages.error(request, "You are not authorized for this action.")
        return redirect("delivery_dashboard")

    if action == "accept":
        order.status = "Out for Delivery"
        msg = f"Order #{order.id} accepted by {request.user.username}"
        title = "Order Accepted"
    else:
        order.status = "Rejected"
        msg = f"Order #{order.id} rejected by {request.user.username}"
        title = "Order Rejected"

    order.save()

    # Notify Admin
    admin_user = User.objects.filter(is_staff=True).first()
    if admin_user:
        Notification.objects.create(
            sender=request.user,
            receiver=admin_user,
            order=order,
            title=title,
            message=msg
        )

    return redirect("delivery:delivery_dashboard")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_link = f"http://127.0.0.1:8000/delivery/reset-password/{uid}/{token}/"

            send_mail(
                "Password Reset",
                f"Click the link to reset your password:\n{reset_link}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            messages.success(request, "Reset link sent to your email!")
            return redirect("delivery:forgot_password")

        except User.DoesNotExist:
            messages.error(request, "Email not found!")

    return render(request, "delivery/forgot_password.html")

def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password = request.POST.get("password")
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successful!")
            return redirect("login")

        return render(request, "reset_password.html")

    else:
        messages.error(request, "Invalid or expired reset link.")
        return redirect("delivery:delivery_login")


def delivery_person_list(request):
    delivery_persons = DeliveryPerson.objects.all()
    return render(request, "delivery_person_list.html", {
        "delivery_persons": delivery_persons
    })

@login_required
def delivery_dashboard(request):
    delivery = request.user.delivery_profile

    orders = Order.objects.filter(delivery_person=delivery)
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    )

    return render(request, "delivery/dashboard.html", {
        "orders": orders,
        "notifications": notifications
    })
