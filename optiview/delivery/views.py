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
from django.db.models import Q
from django.http import JsonResponse
from adminpanel.models import Order
from delivery.models import DeliveryPerson


# =====================================================
# 🔐 DELIVERY ACCESS GUARD
from django.contrib import messages

def delivery_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            messages.error(request, "Please login first")
            return redirect("delivery:delivery_login")

        if request.session.get("panel") != "delivery":
            messages.error(request, "Unauthorized access")
            logout(request)
            request.session.flush()
            return redirect("delivery:delivery_login")

        if not hasattr(request.user, "delivery_profile"):
            messages.error(request, "Delivery account required")
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
# 🔐 LOGIN
# =====================================================
def delivery_login(request):

    if request.user.is_authenticated and is_delivery(request.user):
        return redirect("app:home")

    request.session.flush()

    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),  # ✅ only username
            password=request.POST.get("password"),
        )

        if not user or not hasattr(user, "delivery_profile"):
            messages.error(request, "Invalid username or password")
            return redirect("delivery:delivery_login")

        login(request, user)
        request.session["panel"] = "delivery"
        return redirect("delivery:delivery_dashboard")

    return render(request, "delivery/login.html")

# =====================================================
# 📊 DASHBOARD
# =====================================================
from adminpanel.models import OrderItem
from django.db.models import Q

@login_required(login_url="delivery:delivery_login")
@delivery_required
@login_required(login_url="delivery:delivery_login")
@delivery_required
def delivery_dashboard(request):

    delivery_person = request.user.delivery_profile

    orders = Order.objects.filter(delivery_person=delivery_person)

    # ✅ Sync status
    for order in orders:
        order.update_order_status()

    # ✅ IMPORTANT: exclude rejected from normal flow
    active_orders_qs = orders.exclude(status="rejected")

    context = {
        "total_orders": Order.objects.filter(
            Q(delivery_person=delivery_person) |
            Q(last_rejected_by=delivery_person)
            ).distinct().count(),
        

        # ✅ ONLY ORDER BASED COUNTS (FIX)
        "accepted": active_orders_qs.filter(status="accepted").count(),

        "assigned": active_orders_qs.filter(status="assigned").count(),

        "pending": active_orders_qs.filter(
            status__in=["assigned"]
        ).count(),

        "out_for_delivery": active_orders_qs.filter(
            status="out_for_delivery"
        ).count(),

        "delivered": orders.filter(status__in=["delivered", "partially_delivered"]).count(),

        # ✅ rejected separate
        "rejected": Order.objects.filter(
            last_rejected_by=delivery_person
        ).count(),

        # optional
        "cancelled": OrderItem.objects.filter(
            order__delivery_person=delivery_person,
            status="cancelled"
        ).count(),

        # ✅ active orders list
        "active_orders": active_orders_qs.filter(
            status__in=["accepted", "out_for_delivery"]
        ).order_by('-id')[:5],
    }

    return render(request, "delivery/dashboard.html", context)
from decimal import Decimal
from django.db.models import Q

@login_required(login_url="delivery:delivery_login")
@delivery_required
def my_orders(request):

    delivery_person = request.user.delivery_profile

    orders = Order.objects.filter(
        Q(delivery_person=delivery_person) | 
        Q(last_rejected_by=delivery_person)
    ).prefetch_related("items")

    for order in orders:
        total = Decimal("0.00")

        for item in order.items.all():
            if item.status != "cancelled":
                price = item.price if item.price else item.product.price
                total += price * item.quantity

        # ✅ subtotal
        order.delivered_total = total

        # ✅ delivery logic (same as checkout)
        order.delivery_charge = Decimal("0.00") if total >= 999 else Decimal("50.00")

        # ✅ final total
        order.final_total = total + order.delivery_charge

    return render(request, "delivery/my_orders.html", {
        "orders": orders
    })
# =====================================================
# 👤 PROFILE
# =====================================================
@login_required(login_url="delivery:delivery_login")

@login_required
def delivery_profile(request):

    delivery_person, created = DeliveryPerson.objects.get_or_create(
        user=request.user
    )

    return render(request, "delivery/profile.html", {
        "delivery_person": delivery_person
    })


# =====================================================
# ✏️ EDIT PROFILE
# =====================================================
@login_required(login_url="delivery:delivery_login")
@delivery_required

def edit_profile(request):
    delivery_person, created = DeliveryPerson.objects.get_or_create(
    user=request.user
)

    if request.method == "POST":

        # USER DATA
        request.user.username = request.POST.get("username")
        request.user.email = request.POST.get("email")
        request.user.save()

        # DELIVERY PERSON DATA
        delivery_person.phone = request.POST.get("phone")
        delivery_person.address = request.POST.get("address")

        # IMAGE SAVE
        if request.FILES.get("profile_image"):
            delivery_person.profile_image = request.FILES.get("profile_image")

        delivery_person.save()

        messages.success(request, "Profile updated successfully", extra_tags="profile")

        return redirect("delivery:delivery_profile")

    return render(request, "delivery/edit_profile.html", {
        "delivery_person": delivery_person
    })



from adminpanel.models import OrderItem
from django.contrib.auth.decorators import login_required


@delivery_required
def update_item_status(request, item_id):

    delivery_person = request.user.delivery_profile
    item = get_object_or_404(
    OrderItem,
    id=item_id,
    order__delivery_person=delivery_person
)

    # 🔒 Security check
    if item.order.delivery_person != delivery_person:
        messages.error(request, "You are not assigned to this order.")
        return redirect("delivery:update_status")

    action = request.POST.get("action")

    if action == "accept":
        item.status = "accepted"

    elif action == "out":
        item.status = "out_for_delivery"

    elif action == "complete":
        item.status = "delivered"

    elif action == "reject":
        item.status = "rejected"
        item.order.last_rejected_by = delivery_person

    # 🔥 ADD THIS
        item.order.status = "rejected"

        item.order.save(update_fields=["last_rejected_by", "status"])

    item.save()


    # 🔥 Update parent order automatically
    item.order.update_order_status()

    return redirect("delivery:update_status")

def update_orders_page(request):

    delivery_person = request.user.delivery_profile

    orders = Order.objects.filter(
    delivery_person=delivery_person
).exclude(status="rejected")

    return render(request, "delivery/update_status.html", {
        "orders": orders,
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from decimal import Decimal


@login_required

@delivery_required


def update_status(request):

    delivery_person = request.user.delivery_profile

    orders = Order.objects.filter(
        delivery_person=delivery_person
    ).prefetch_related("items")

    for order in orders:
        total = Decimal("0.00")

        for item in order.items.all():

            status = (item.status or "").strip().lower()

            # ❌ skip cancelled
            if status == "cancelled":
                continue

        # ✅ always calculate fresh
            price = item.price or item.product.price or Decimal("0.00")

            total += price * item.quantity

    # 🔥 DEBUG (REMOVE AFTER TEST)
        print("ORDER:", order.id, "TOTAL:", total)

        order.delivered_total = total

    # ✅ FIX DELIVERY LOGIC
        if total >= Decimal("999"):
            order.delivery_charge = Decimal("0.00")
        else:
            order.delivery_charge = Decimal("50.00")

        order.final_total = total + order.delivery_charge
    # ✅ counts (unchanged)
    PENDING_STATUSES = ["assigned", "accepted"]

    context = {
        "orders": orders,
        "pending_count": orders.filter(status__in=PENDING_STATUSES).count(),
        "assigned_count": orders.filter(status="assigned").count(),
        "out_count": orders.filter(status="out_for_delivery").count(),
        "delivered_count": orders.filter(status="delivered").count(),
    }

    return render(request, "delivery/update_status.html", context)
@login_required(login_url="delivery:delivery_login")
@delivery_required
def accepted_orders(request):
    delivery_person = request.user.delivery_profile

    orders = Order.objects.filter(
        delivery_person=delivery_person,
        status="accepted"
    )
    return render(request, "delivery/accepted_orders.html", {"orders": orders})

@login_required(login_url="delivery:delivery_login")
@delivery_required
def rejected_orders(request):
    delivery_person = request.user.delivery_profile

    orders = Order.objects.filter(
        last_rejected_by=delivery_person   # ✅ FIX
    )

    return render(request, "delivery/rejected_orders.html", {"orders": orders})
from adminpanel.models import OrderItem

@login_required(login_url="delivery:delivery_login")
@delivery_required
def cancelled_orders(request):

    delivery_person = request.user.delivery_profile

    items = OrderItem.objects.filter(
        order__delivery_person=delivery_person,
        status="cancelled"
    )

    return render(request, "delivery/cancelled_orders.html", {
        "items": items
    })

@login_required(login_url="delivery:delivery_login")
@delivery_required
def assigned_orders(request):
    delivery_person = request.user.delivery_profile

    orders = Order.objects.filter(
        delivery_person=delivery_person,
        status="assigned"
    )
    return render(request, "delivery/assigned_orders.html", {"orders": orders})

@login_required(login_url="delivery:delivery_login")
@delivery_required
def pending_orders(request):

    delivery_person = request.user.delivery_profile

    orders = Order.objects.filter(
        delivery_person=delivery_person,   # 🔥 MAIN FIX
        status__in=[ "assigned"]
    )

    return render(request, "delivery/pending_orders.html", {"orders": orders})

@login_required(login_url="delivery:delivery_login")
@delivery_required
def out_of_delivery_orders(request):
    delivery_person = request.user.delivery_profile

    orders = Order.objects.filter(
        delivery_person=delivery_person,
        status="out_for_delivery"
    )
    return render(request, "delivery/out_of_delivery_orders.html", {"orders": orders})

from decimal import Decimal
from django.contrib.auth.decorators import login_required

@login_required(login_url="delivery:delivery_login")
@delivery_required
def delivered_orders(request):
    delivery_person = request.user.delivery_profile

    orders = Order.objects.filter(
        delivery_person=delivery_person,
        status__in=["delivered", "partially_delivered"]
    )

    for order in orders:
        total = Decimal("0.00")

        for item in order.items.all():
            if item.status != "cancelled":

                price = item.price if item.price else item.product.price  # ✅ FIX

                total += price * item.quantity

        order.delivered_total = total

    return render(request, "delivery/delivered_orders.html", {
        "orders": orders
    })


@require_POST
@login_required
@delivery_required

def accept_reject_order(request, order_id):

    delivery_person = request.user.delivery_profile
    order = get_object_or_404(Order, id=order_id, delivery_person=delivery_person)

    if request.method == "POST":
        action = request.POST.get("action")

        items = order.items.all()

        if action == "accept":

            for item in items:
                if item.status != "cancelled":
                    item.status = "accepted"
                    item.save()

            order.status = "accepted"
            order.save()   # ✅ VERY IMPORTANT

        elif action == "reject":

            for item in items:
                if item.status != "cancelled":
                    item.status = "rejected"
                    item.save()

            order.status = "rejected"
            order.last_rejected_by = delivery_person
            order.delivery_person = None
            order.save()   # ✅ SAVE

    return redirect("delivery:update_status")
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def delivery_change_password(request):

    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = request.user

        # ✅ Old password check
        if not user.check_password(old_password):
            messages.error(request, "Old password is incorrect")
            return redirect("delivery:delivery_change_password")

        # ✅ Password length
        if len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters")
            return redirect("delivery:delivery_change_password")

        # ✅ Confirm password
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("delivery:delivery_change_password")

        # ✅ Save new password
        user.set_password(new_password)
        user.save()

        # ✅ Keep user logged in
        update_session_auth_hash(request, user)

        messages.success(request, "Password changed successfully")
        return redirect("delivery:delivery_profile")

    return render(request, "delivery/change_password.html")



import random
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from adminpanel.models import OTPCode

def delivery_forgot_password(request):

    if request.method == "POST":

        email = request.POST.get("email")

        users = User.objects.filter(email=email)

        if not users.exists():
            return render(request, "delivery/forgot_password.html", {
                "error": "No account found with this email."
            })

        user = users.first()

        # Generate OTP
        otp = random.randint(100000, 999999)

        OTPCode.objects.filter(user=user, verified=False).delete()

        # Save OTP
        OTPCode.objects.create(
            user=user,
            code=otp,
            expires_at=timezone.now() + timedelta(minutes=5)
        )

        # Send email
        send_mail(
            subject="Delivery Password Reset OTP",
            message=f"Your OTP code is: {otp}. It will expire in 5 minutes.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        return redirect(f"{reverse('delivery:delivery_verify_otp')}?email={email}")

    return render(request, "delivery/forgot_password.html")
  
def delivery_verify_otp(request):

    email = request.GET.get("email")

    if request.method == "POST":

        email = request.POST.get("email")
        otp_input = request.POST.get("otp")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Convert OTP to integer safely
        try:
            otp_input = int(otp_input)
        except:
            return render(request, "delivery/verify_otp.html", {
                "error": "Invalid OTP format.",
                "email": email
            })

        users = User.objects.filter(email=email)

        if not users.exists():
            return render(request, "delivery/verify_otp.html", {
                "error": "Invalid email or OTP.",
                "email": email
            })

        user = users.first()

        otp_record = OTPCode.objects.filter(
            user=user,
            code=otp_input,
            verified=False
        ).order_by("-id").first()

        # OTP check
        if not otp_record or otp_record.is_expired():
            return render(request, "delivery/verify_otp.html", {
                "error": "OTP expired or invalid.",
                "email": email
            })

        # Password match check
        if new_password != confirm_password:
            return render(request, "delivery/verify_otp.html", {
                "error": "Passwords do not match.",
                "email": email
            })

        # Password length check
        if len(new_password) < 6:
            return render(request, "delivery/verify_otp.html", {
                "error": "Password must be at least 6 characters.",
                "email": email
            })

        # Reset password
        user.set_password(new_password)
        user.save()

        # Mark OTP verified
        otp_record.verified = True
        otp_record.save()

        messages.success(request, "Password reset successful. Please login.")

        return redirect("delivery:delivery_login")

    return render(request, "delivery/verify_otp.html", {
        "email": email
    })