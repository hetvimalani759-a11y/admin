from datetime import date
from itertools import product
from urllib import request

from django.utils.timezone import now, timedelta
from django.db.models.functions import TruncDate, TruncMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.db.models import Sum, Q, Count
from django.contrib.auth.models import User
from adminpanel.utils import is_admin
import json
from django.utils import timezone
from delivery.models import DeliveryPerson


User = get_user_model()
from .models import (
    Product, Category, SubCategory, Offer,
    Order, OrderItem, Lens,Review,
    CompanyInfo,DashboardImage,ProductVariant,
    ProductVariantImage,FrameType,FrameShape,Brand,Color,Purchase,Material
)
# ✅ CORRECT
from adminpanel.models import Notification

LOW_STOCK_THRESHOLD = 50


# =====================================================
# 🔐 AUTH
# =====================================================

def admin_login(request):
    # if request.user.is_authenticated and is_admin(request.user):
    #     return redirect("adminpanel:dashboard")
    # request.session.flush()

    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        if user and is_admin(user):
            login(request, user)
            messages.success(request, "Welcome Admin")
            return redirect("adminpanel:dashboard")

        messages.error(request, "Admin login only!")

    return render(request, "admin/login.html")
import random
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from adminpanel.models import OTPCode
from django.conf import settings 


def admin_forgot_password(request):

    if request.method == "POST":

        email = request.POST.get("email")

        users = User.objects.filter(email=email)

        if not users.exists():
            return render(request, "admin/forgot_password.html", {
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
            subject="Admin Password Reset OTP",
            message=f"Your OTP code is: {otp}. It will expire in 5 minutes.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        return redirect(f"{reverse('adminpanel:verify_otp')}?email={email}")

    return render(request, "admin/forgot_password.html")


  
def admin_verify_otp(request):

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
            return render(request, "admin/verify_otp.html", {
                "error": "Invalid OTP format.",
                "email": email
            })

        users = User.objects.filter(email=email)

        if not users.exists():
            return render(request, "admin/verify_otp.html", {
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
            return render(request, "admin/verify_otp.html", {
                "error": "OTP expired or invalid.",
                "email": email
            })

        # Password match check
        if new_password != confirm_password:
            return render(request, "admin/verify_otp.html", {
                "error": "Passwords do not match.",
                "email": email
            })

        # Password length check
        if len(new_password) < 6:
            return render(request, "admin/verify_otp.html", {
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

        return redirect("adminpanel:login")

    return render(request, "admin/verify_otp.html", {
        "email": email
    })

from .models import AdminProfile
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required
def admin_profile(request):
    profile, created = AdminProfile.objects.get_or_create(user=request.user)
    return render(request, "admin/profile.html", {"profile": profile})


from datetime import date
from django.contrib import messages
from datetime import date
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import AdminProfile

def edit_profile(request):

    profile, created = AdminProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        dob = request.POST.get("dob")
        address = request.POST.get("address")

        # DOB validation (future date not allowed)
        if dob:
            if date.fromisoformat(dob) > date.today():
                messages.error(request, "Future date is not allowed for Date of Birth")
                return redirect("adminpanel:edit_profile")

        # Update user fields
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.save()

        # Update profile fields
        profile.phone = phone
        profile.date_of_birth = dob
        profile.address = address

        # Profile image upload
        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES.get("profile_image")

        profile.save()

        messages.success(request, "Profile updated successfully ✅")
        return redirect("adminpanel:admin_profile")

    return render(request,"admin/edit_profile.html",{
        "profile": profile,
        "today": date.today()
    })


from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def change_password(request):

    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = request.user

        # check old password
        if not check_password(old_password, user.password):
            messages.error(request, "Old password is incorrect")
            return redirect("adminpanel:change_password")

        # password length check
        if len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters")
            return redirect("adminpanel:change_password")

        # confirm password check
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("adminpanel:change_password")

        user.set_password(new_password)
        user.save()

        update_session_auth_hash(request, user)

        messages.success(request, "Password changed successfully")
        return redirect("adminpanel:admin_profile")

    return render(request, "admin/change_password.html")

    
@login_required(login_url="adminpanel:login")
@login_required
def admin_logout(request):
    request.session.flush()
    logout(request)
    return redirect("adminpanel:login")
from django.shortcuts import render, redirect
from .models import DashboardImage

def add_dashboard_image(request):
    if request.method == 'POST':
        image = request.FILES.get('image')

        if image:
            DashboardImage.objects.create(
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                image=image
            )
            return redirect('adminpanel:add_dashboard_image')  # reload same page

    images = DashboardImage.objects.all().order_by("-id")

    return render(request, 'admin/add_dashboard_image.html', {
        "images": images
    })
from django.shortcuts import render, redirect, get_object_or_404
from .models import DashboardImage

def edit_dashboard_image(request, id):
    image_obj = get_object_or_404(DashboardImage, id=id)

    if request.method == "POST":
        image_obj.title = request.POST.get("title")
        image_obj.description = request.POST.get("description")

        # if new image uploaded
        if request.FILES.get("image"):
            image_obj.image = request.FILES.get("image")

        image_obj.save()
        return redirect("adminpanel:add_dashboard_image")

    return render(request, "admin/edit_dashboard_image.html", {
        "image": image_obj
    })
def delete_dashboard_image(request, id):
    image_obj = get_object_or_404(DashboardImage, id=id)
    image_obj.delete()
    return redirect("adminpanel:add_dashboard_image")


from django.http import JsonResponse
from django.contrib.auth.models import User

def toggle_user(request, id):
    user = User.objects.get(id=id)
    user.is_active = not user.is_active
    user.save()

    return JsonResponse({
        "status": "Active" if user.is_active else "Inactive"
    })
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

User = get_user_model()

def delete_user(request, id):
    user = User.objects.get(id=id)
    user.is_active = False   # ✅ deactivate instead of delete
    user.save()
    return redirect('adminpanel:user_list')
# =====================================================
# 📊 DASHBOARD
# =====================================================
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from decimal import Decimal
from django.db.models.functions import TruncDate
# ✅ CORRECT
from adminpanel.models import Notification
@user_passes_test(is_admin, login_url="adminpanel:login")
def dashboard(request):
    # ---------- TOTAL COUNTS ----------
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_lenses = Lens.objects.count()
    total_users = User.objects.count()
    

    total_revenue = OrderItem.objects.filter(
    status="delivered",                  # ✅ only delivered items
    return_status__in=["none", "rejected"],
    refund_status="none"
).aggregate(
    total=Sum(
        ExpressionWrapper(
            F("quantity") * F("price"),
            output_field=DecimalField()
        )
    )
)["total"] or Decimal("0")
    # ---------- LATEST PRODUCT ----------
    latest_products = Product.objects.order_by("-created_at")[:1]

    # ---------- COMPANY INFO ----------
    company = CompanyInfo.objects.first()

    # ---------- NOTIFICATIONS ----------
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    notification_count = notifications.count()

    # ---------- LOW STOCK PRODUCTS ----------
    # Precompute purchased and sold quantities
    low_stock_variants = ProductVariant.objects.filter(
    stock__lte=LOW_STOCK_THRESHOLD
)

    low_stock_count = low_stock_variants.count()
    # low_stock_count = len(low_stock_products)
    # 🔔 Trigger toast notification
    if low_stock_variants.exists():
        messages.warning(
            request,
            f"{low_stock_variants.count()} variant(s) are below {LOW_STOCK_THRESHOLD} stock!"
        )

    # ---------- ORDER STATUS PIE ----------
    order_qs = Order.objects.values("status").annotate(count=Count("id"))
    order_labels = [o["status"].title() for o in order_qs]
    order_values = [o["count"] for o in order_qs]

    # ---------- WEEKLY REVENUE LINE ----------
    today = now().date()
    start_week = today - timedelta(days=today.weekday())

    

    revenue_qs = (
    OrderItem.objects
    .filter(
        order__created_at__date__gte=start_week,
        status="delivered",
        return_status__in=["none", "rejected"],
        refund_status="none"
    )
    .annotate(day=TruncDate("order__created_at"))
    .values("day")
    .annotate(
        total=Sum(
            ExpressionWrapper(
                F("quantity") * F("price"),
                output_field=DecimalField()
            )
        )
    )
)

    revenue_map = {r["day"]: float(r["total"]) for r in revenue_qs}

    weekly_labels = []
    weekly_data = []

    for i in range(7):
        day = start_week + timedelta(days=i)
        weekly_labels.append(day.strftime("%a"))
        weekly_data.append(revenue_map.get(day, 0))

    # ---------- CONTEXT ----------
    context = {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_lenses": total_lenses,
        "total_users": total_users,
        "total_revenue": total_revenue,
        "latest_products": latest_products,
        "company": company,
        "notifications": notifications,
        "notification_count": notification_count,
        "low_stock": low_stock_count,
        "order_labels": json.dumps(order_labels),
        "order_values": json.dumps(order_values),
        "weekly_labels": json.dumps(weekly_labels),
        "weekly_data": json.dumps(weekly_data),
    }

    return render(request, "admin/dashboard.html", context)

  # adjust as needed
  

def notification_count(request):
    if request.user.is_authenticated:
        return {
            "notification_count": Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count()
        }
    return {"notification_count": 0}

from .models import ProductVariant

LOW_STOCK_THRESHOLD = 50

def low_stock_alert(request):
    if not request.path.startswith("/admin-panel/"):
        return {}

    low_variants = ProductVariant.objects.filter(
        stock__lte=LOW_STOCK_THRESHOLD
    ).select_related("product", "color")

    return {
        "low_stock_variants": low_variants,
        "low_stock_threshold": LOW_STOCK_THRESHOLD,
    }
   
from .models import Product, Purchase, ProductVariant, Brand, Color
def add_purchase_page(request):
    products = Product.objects.filter(is_active=True)
    variants = ProductVariant.objects.all()  # all variants for selection
    brands = Brand.objects.all()
    colors = Color.objects.all()

    if request.method == "POST":
        product_id = request.POST.get("product")
        variant_id = request.POST.get("variant")  # new
        dealer_name = request.POST.get("dealer_name")
        quantity = request.POST.get("quantity")
        cost_price = request.POST.get("cost_price")

        if product_id and dealer_name and quantity:
            product = Product.objects.get(id=product_id)
            variant = ProductVariant.objects.get(id=variant_id) if variant_id else None

            Purchase.objects.create(
                product=product,
                variant=variant,
                dealer_name=dealer_name,
                quantity=int(quantity),
                cost_price=float(cost_price) if cost_price else None
            )
            return redirect('adminpanel:add_purchase_page')

    return render(request, "admin/add_purchase.html", {
        "products": products,
        "variants": variants,
        "brands": brands,
        "colors": colors
    })
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
from .models import Dealer, Purchase, PurchaseItem, ProductVariant

from django.shortcuts import render, redirect
from .models import Dealer

def dealer_list(request):
    dealers = Dealer.objects.all()
    return render(request, 'admin/dealer_list.html', {'dealers': dealers})

def add_dealer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        Dealer.objects.create(name=name, email=email, phone=phone, address=address)
        return redirect('adminpanel:dealer_list')
    
    return render(request, 'admin/add_dealer.html')
def edit_dealer(request, dealer_id):
    dealer = get_object_or_404(Dealer, id=dealer_id)

    if request.method == 'POST':
        dealer.name = request.POST.get('name')
        dealer.email = request.POST.get('email')
        dealer.phone = request.POST.get('phone')
        dealer.address = request.POST.get('address')
        dealer.save()
        messages.success(request, "Dealer updated successfully!")
        return redirect('adminpanel:dealer_list')

    return render(request, 'admin/edit_dealer.html', {'dealer': dealer})

def delete_dealer(request, dealer_id):
    dealer = get_object_or_404(Dealer, id=dealer_id)
    if request.method == 'POST':
        dealer.delete()
        messages.success(request, "Dealer deleted successfully!")
    return redirect('adminpanel:dealer_list')

def check_product_name(request):
    name = request.GET.get('name', '').strip()
    exists = Product.objects.filter(name__iexact=name).exists()
    return JsonResponse({'exists': exists})
@transaction.atomic
def add_purchase(request):
    dealers = Dealer.objects.all()
    variants = ProductVariant.objects.all()

    if request.method == "POST":
        dealer_id = request.POST.get("dealer")
        bill_number = request.POST.get("bill_number")

        purchase = Purchase.objects.create(
            dealer_id=dealer_id,
            bill_number=bill_number
        )

        total_amount = 0

        variant_ids = request.POST.getlist("variant")
        quantities = request.POST.getlist("quantity")
        prices = request.POST.getlist("cost_price")

        for i in range(len(variant_ids)):
            variant = ProductVariant.objects.get(id=variant_ids[i])
            qty = int(quantities[i])
            price = float(prices[i])

            # Create purchase item
            PurchaseItem.objects.create(
                purchase=purchase,
                variant=variant,
                quantity=qty,
                cost_price=price
            )

            # 🔥 Increase stock
            variant.stock += qty
            variant.save()

            total_amount += qty * price

        purchase.total_amount = total_amount
        purchase.save()

        messages.success(request, "Purchase added successfully!")
        return redirect("adminpanel:add_purchase")

    return render(request, "admin/add_purchase.html", {
        "dealers": dealers,
        "variants": variants
    })
@transaction.atomic
def delete_purchase(request, id):
    purchase = get_object_or_404(Purchase, id=id)

    if request.method == "POST":
        for item in purchase.items.all():
            item.variant.stock -= item.quantity
            item.variant.save()

        purchase.delete()
        messages.success(request, "Purchase deleted successfully!")

    return redirect("adminpanel:purchase_list")
def purchase_list(request):
    purchases = Purchase.objects.all().order_by("-purchase_date")
    return render(request, "admin/purchase_list.html", {
        "purchases": purchases
    })

from django.db import transaction

@transaction.atomic


def edit_purchase(request, id):
    purchase = get_object_or_404(Purchase, id=id)
    dealers = Dealer.objects.all()
    variants = ProductVariant.objects.all()

    if request.method == "POST":
        # 1️⃣ Reverse old stock first
        for item in purchase.items.all():
            item.variant.stock -= item.quantity
            item.variant.save()

        # 2️⃣ Delete old items
        purchase.items.all().delete()

        # 3️⃣ Update dealer & bill
        purchase.dealer_id = request.POST.get("dealer")
        purchase.bill_number = request.POST.get("bill_number")
        purchase.save()

        total_amount = 0

        # 4️⃣ Handle existing items (variant[])
        variant_ids = request.POST.getlist("variant[]")
        quantities = request.POST.getlist("quantity[]")
        prices = request.POST.getlist("cost_price[]")

        for i in range(len(variant_ids)):
            variant = ProductVariant.objects.get(id=variant_ids[i])
            qty = int(quantities[i])
            price = float(prices[i])

            PurchaseItem.objects.create(
                purchase=purchase,
                variant=variant,
                quantity=qty,
                cost_price=price
            )

            variant.stock += qty
            variant.save()
            total_amount += qty * price

        # 5️⃣ Handle new items (new_variant[])
        new_variant_ids = request.POST.getlist("new_variant[]")
        new_quantities = request.POST.getlist("new_quantity[]")
        new_prices = request.POST.getlist("new_cost_price[]")

        for i in range(len(new_variant_ids)):
            variant = ProductVariant.objects.get(id=new_variant_ids[i])
            qty = int(new_quantities[i])
            price = float(new_prices[i])

            PurchaseItem.objects.create(
                purchase=purchase,
                variant=variant,
                quantity=qty,
                cost_price=price
            )

            variant.stock += qty
            variant.save()
            total_amount += qty * price

        purchase.total_amount = total_amount
        purchase.save()

        messages.success(request, "Purchase updated successfully!")
        return redirect("adminpanel:purchase_list")

    return render(request, "admin/edit_purchase.html", {
        "purchase": purchase,
        "dealers": dealers,
        "variants": variants
    })
def stock_report(request):
    variants = ProductVariant.objects.all()
    return render(request, "admin/stock_report.html", {
        "variants": variants
    })
from django.db.models import Sum, F

def profit_report(request):
    items = PurchaseItem.objects.all()

    total_purchase = sum(item.get_total() for item in items)

    variants = ProductVariant.objects.all()
    total_stock_value = sum(v.stock * v.product.price for v in variants)
    estimated_profit = total_stock_value - total_purchase
    return render(request, "admin/profit_report.html", {
        "total_purchase": total_purchase,
        "total_stock_value": total_stock_value,
        "estimated_profit": estimated_profit
    })
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
from django.http import HttpResponse


def purchase_invoice(request, id):
    purchase = get_object_or_404(Purchase, id=id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="purchase_{purchase.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=pagesizes.A4)
    elements = []

    styles = getSampleStyleSheet()

    elements.append(Paragraph(f"Purchase Invoice", styles["Heading1"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Dealer: {purchase.dealer.name}", styles["Normal"]))
    elements.append(Paragraph(f"Bill No: {purchase.bill_number}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    data = [["Product", "Qty", "Cost", "Total"]]

    for item in purchase.items.all():
        data.append([
            item.variant.product.name,
            item.quantity,
            item.cost_price,
            item.get_total()
        ])

    table = Table(data)
    table.setStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ])

    elements.append(table)
    doc.build(elements)

    return response

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import PurchaseReturn, PurchaseItem

def purchase_return_list(request):
    """List all purchase returns"""
    returns = PurchaseReturn.objects.select_related('purchase_item__variant').all().order_by('-return_date')
    return render(request, 'admin/purchase_return_list.html', {'returns': returns})


def add_purchase_return(request):
    """Add a new purchase return"""
    if request.method == "POST":
        purchase_item_id = request.POST.get('purchase_item')
        quantity = request.POST.get('quantity')
        reason = request.POST.get('reason', '')

        if not purchase_item_id or not quantity:
            messages.error(request, "Please select item and enter quantity.")
            return redirect('adminpanel:add_purchase_return')

        purchase_item = get_object_or_404(PurchaseItem, id=purchase_item_id)
        quantity = int(quantity)

        if quantity > purchase_item.variant.stock:
            messages.error(request, "Return quantity cannot exceed available stock.")
            return redirect('adminpanel:add_purchase_return')

        purchase_return = PurchaseReturn(
            purchase_item=purchase_item,
            quantity=quantity,
            reason=reason
        )
        try:
            purchase_return.save()
            messages.success(request, f"Returned {quantity} units of {purchase_item.variant} successfully.")
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect('adminpanel:purchase_return_list')

    # GET request
    purchase_items = PurchaseItem.objects.select_related('variant', 'purchase').all()
    return render(request, 'admin/add_purchase_return.html', {'purchase_items': purchase_items})

# ===== Add Brand =====
from django.shortcuts import render, redirect, get_object_or_404
from .models import Brand
from django.contrib import messages

# -------------------------------
# Add Brand Page
# -------------------------------
def add_brand_page(request):
    brands = Brand.objects.all().order_by('-id')  # Show latest first

    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Brand.objects.create(name=name)
            messages.success(request, f"Brand '{name}' added successfully!")
            return redirect('adminpanel:add_brand')
        else:
            messages.error(request, "Brand name cannot be empty.")

    return render(request, "admin/add_brand.html", {"brands": brands})


# -------------------------------
# Edit Brand
# -------------------------------
def edit_brand(request, id):
    brand = get_object_or_404(Brand, id=id)

    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            brand.name = name
            brand.save()
            messages.success(request, f"Brand '{name}' updated successfully!")
            return redirect('adminpanel:add_brand')
        else:
            messages.error(request, "Brand name cannot be empty.")

    return render(request, "admin/edit_brand.html", {"brand": brand})


# -------------------------------
# Delete Brand
# -------------------------------
def delete_brand(request, id):
    brand = get_object_or_404(Brand, id=id)

    if request.method == 'POST':
        brand_name = brand.name
        brand.delete()
        messages.success(request, f"Brand '{brand_name}' deleted successfully!")
        return redirect('adminpanel:add_brand')

    return redirect('adminpanel:add_brand')  # fallback if GET

# ===== Add Color =====
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from .models import Color
def add_color_page(request):
    colors = Color.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        code = request.POST.get("code")

        if name:
            try:
                Color.objects.create(name=name, code=code)
                messages.success(request, "Color added successfully ✅")

            except ValidationError:
                messages.error(request, "Invalid color name ❌")

            except Exception:
                messages.error(request, "Something went wrong ⚠")

        else:
            messages.error(request, "Color name is required ❌")

        return redirect('adminpanel:add_color_page')

    return render(request, "admin/add_color.html", {"colors": colors})
@login_required
def edit_color(request, pk):
    color = get_object_or_404(Color, pk=pk)

    if request.method == "POST":
        color.name = request.POST.get("name")
        color.save()
        messages.success(request, "Color updated successfully.")
        return redirect("adminpanel:add_color_page")

    return render(request, "admin/edit_color.html", {"color": color})

@login_required
def delete_color(request, pk):
    color = get_object_or_404(Color, pk=pk)
    color.delete()
    messages.success(request, "Color deleted successfully.")
    return redirect("adminpanel:add_color_page")

# =====================================================
# 🔔 NOTIFICATIONS
# =====================================================
# ✅ USE THIS
from adminpanel.models import Notification
@user_passes_test(is_admin, login_url="adminpanel:login")
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-id")
    return render(request, "admin/notifications.html", {"notifications": notifications})


@user_passes_test(is_admin, login_url="adminpanel:login")
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"status": "ok"})
# ✅ CORRECT
from adminpanel.models import Notification

@user_passes_test(is_admin, login_url="adminpanel:login")
def add_notification(request):
    if request.method == "POST":
        title = request.POST.get("title")
        message = request.POST.get("message")
        for user in User.objects.all():
            Notification.objects.create(user=user, title=title, message=message)
        return redirect("adminpanel:notifications")
    return render(request, "admin/add_notification.html")


# =====================================================
# 📦 CATEGORY
# =====================================================

@user_passes_test(is_admin, login_url="adminpanel:login")


def add_category(request):
    categories = Category.objects.all().order_by("-id")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        image = request.FILES.get("image")  # <-- handle uploaded image

        if name:
            category, created = Category.objects.get_or_create(name=name)
            if image:
                category.image = image
                category.save()
            if created:
                messages.success(request, "Category added successfully")
            else:
                messages.info(request, "Category already exists")
        else:
            messages.error(request, "Please enter a category name")

        return redirect("adminpanel:add_category")

    return render(request, "admin/add_category.html", {"categories": categories})


@user_passes_test(is_admin, login_url="adminpanel:login")
# views.py
def edit_category(request, id):
    category = Category.objects.get(id=id)

    if request.method == "POST":
        name = request.POST.get("name")
        image = request.FILES.get("image")

        category.name = name
        if image:  # only update if a new image is uploaded
            category.image = image

        category.save()
        messages.success(request, "Category updated successfully!")
        return redirect('adminpanel:add_category')

    return render(request, "admin/edit_category.html", {"category": category})


@user_passes_test(is_admin, login_url="adminpanel:login")
def delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    messages.success(request, "Category deleted successfully")
    return redirect("adminpanel:add_category")


# =====================================================
# 📦 SUBCATEGORY
# =====================================================
@user_passes_test(is_admin, login_url="adminpanel:login")
def add_subcategory(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.select_related("category").all()
    
    if request.method == "POST":
        allow_lens = True if request.POST.get("allow_lens") == "on" else False
        SubCategory.objects.create(
            category_id=request.POST.get("category"),
            name=request.POST.get("name"),
            allow_lens=allow_lens
        
        )
        messages.success(request, "SubCategoery added sucessfully")
        return redirect("adminpanel:add_subcategory")
    return render(request, "admin/add_subcategory.html", {
        "categories": categories,
        "subcategories": subcategories
    })


@user_passes_test(is_admin, login_url="adminpanel:login")
def edit_subcategory(request, id):
    subcategory = get_object_or_404(SubCategory, id=id)
    categories = Category.objects.all()
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        category_id = request.POST.get("category")
        allow_lens = True if request.POST.get("allow_lens") == "on" else False
        if name and category_id:
            subcategory.name = name
            subcategory.category_id = category_id
            subcategory.allow_lens = allow_lens
            subcategory.save()
            messages.success(request, "Subcategory updated successfully")
        return redirect("adminpanel:add_subcategory")
    return render(request, "admin/edit_subcategory.html", {
        "subcategory": subcategory,
        "categories": categories
    })


@user_passes_test(is_admin, login_url="adminpanel:login")
def delete_subcategory(request, id):
    subcategory = get_object_or_404(SubCategory, id=id)
    subcategory.delete()
    messages.success(request, "Subcategory deleted successfully")
    return redirect("adminpanel:add_subcategory")


@login_required
def get_subcategories(request, category_id):
    subcats = SubCategory.objects.filter(category_id=category_id)
    return JsonResponse([{"id": s.id, "name": s.name} for s in subcats], safe=False)


# =====================================================
# 📦 PRODUCTS
# =====================================================


@user_passes_test(is_admin, login_url="adminpanel:login")
def product_list(request):
    search = request.GET.get("search", "")
    products = Product.objects.all()

    # Filter by search
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(brand__name__icontains=search) |  # Fix: search by brand name
            Q(price__icontains=search)
        )

    # Annotate total stock from variants
    products = products.annotate(
        total_stock=Sum('variants__stock')
    ).prefetch_related('variants')  # optional: improves color loop performance

    return render(request, "admin/product_list.html", {
        "products": products,
        "search": search
    })

def add_frame_type(request):
    if request.method == "POST":
        name = request.POST.get("name")

        if name:
            FrameType.objects.create(name=name)
            return redirect("adminpanel:frame_type_list")  # tame je url name mukyu hoy

    return render(request, "admin/add_frame_type.html")
@login_required
def edit_frame_type(request, pk):
    frame_type = get_object_or_404(FrameType, pk=pk)

    if request.method == "POST":
        frame_type.name = request.POST.get("name")
        frame_type.save()
        messages.success(request, "Frame type updated successfully.")
        return redirect("adminpanel:frame_type_list")

    return render(request, "admin/edit_frame_type.html", {"frame_type": frame_type})


@login_required
def delete_frame_type(request, pk):
    frame_type = get_object_or_404(FrameType, pk=pk)
    frame_type.delete()
    messages.success(request, "Frame type deleted successfully.")
    return redirect("adminpanel:frame_type_list")

def frame_type_list(request):
    frame_types = FrameType.objects.all()
    return render(request, "admin/frame_type_list.html", {
        "frame_types": frame_types
    })
def frame_shape_list(request):
    shapes = FrameShape.objects.all()
    return render(request, "admin/frame_shape_list.html", {"shapes": shapes})
def add_frame_shape(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            FrameShape.objects.create(name=name)
            messages.success(request, "Frame Shape added successfully!")
            return redirect("adminpanel:frame_shape_list")

    return render(request, "admin/add_frame_shape.html")
@login_required
def edit_frame_shape(request, pk):
    frame_shape = get_object_or_404(FrameShape, pk=pk)

    if request.method == "POST":
        frame_shape.name = request.POST.get("name")
        frame_shape.save()
        messages.success(request, "Frame shape updated successfully.")
        return redirect("adminpanel:frame_shape_list")

    return render(request, "admin/edit_frame_shape.html", {"frame_shape": frame_shape})


@login_required
def delete_frame_shape(request, pk):
    frame_shape = get_object_or_404(FrameShape, pk=pk)
    frame_shape.delete()
    messages.success(request, "Frame shape deleted successfully.")
    return redirect("adminpanel:frame_shape_list")

def add_material(request):
    if request.method == "POST":
        name = request.POST.get("name")

        if name:
            Material.objects.create(name=name)
            messages.success(request, "Material added successfully!")
            return redirect("adminpanel:add_material")

    materials = Material.objects.all()
    return render(request, "admin/add_material.html", {"materials": materials})
@user_passes_test(is_admin, login_url="adminpanel:login")
@login_required
def edit_material(request, pk):
    material = get_object_or_404(Material, pk=pk)

    if request.method == "POST":
        material.name = request.POST.get("name")
        material.save()
        messages.success(request, "Material updated successfully.")
        return redirect("adminpanel:add_material")

    return render(request, "admin/edit_material.html", {"material": material})


@login_required
def delete_material(request, pk):
    material = get_object_or_404(Material, pk=pk)
    material.delete()
    messages.success(request, "Material deleted successfully.")
    return redirect("adminpanel:add_material")


def add_product(request):
    categories = Category.objects.all()
    brands = Brand.objects.all()
    colors = Color.objects.all()
    frame_types = FrameType.objects.all()
    frame_shapes = FrameShape.objects.all()
    materials = Material.objects.all()

    if request.method == "POST":

        # ✅ Frame Type
        frame_type_obj = None
        frame_type_id = request.POST.get("frame_type")
        if frame_type_id:
            try:
                frame_type_obj = FrameType.objects.get(id=frame_type_id)
            except FrameType.DoesNotExist:
                pass

        # ✅ Frame Shape
        frame_shape_obj = None
        frame_shape_id = request.POST.get("frame_shape")
        if frame_shape_id:
            try:
                frame_shape_obj = FrameShape.objects.get(id=frame_shape_id)
            except FrameShape.DoesNotExist:
                pass

        # ✅ Material
        material_obj = None
        material_id = request.POST.get("material")
        if material_id:
            try:
                material_obj = Material.objects.get(id=material_id)
            except Material.DoesNotExist:
                pass

        # ✅ Create Product (NO stock here)
        product = Product.objects.create(
            name=request.POST.get("name"),
            brand_id=request.POST.get("brand"),
            price=request.POST.get("price"),
            category_id=request.POST.get("category"),
            subcategory_id=request.POST.get("subcategory"),
            description=request.POST.get("description"),
            frame_type=frame_type_obj,
            frame_shape=frame_shape_obj,
            material=material_obj,
        )

        # ✅ Parse Variants
        import re
        variant_data = {}

        for key, value in request.POST.items():
            m = re.match(r"variants\[(\d+)\]\[(\w+)\]", key)
            if m:
                index, field = m.groups()
                if index not in variant_data:
                    variant_data[index] = {}
                variant_data[index][field] = value

        # ✅ Create Variants
        for index, variant in variant_data.items():
            color_id = variant.get("color")
            stock = int(variant.get("stock", 0))

            variant_obj = ProductVariant.objects.create(
                product=product,
                color_id=color_id,
                stock=stock,
            )

            # ✅ Attach Images
            images = request.FILES.getlist(f"variants[{index}][images][]")
            for img in images:
                ProductVariantImage.objects.create(
                    variant=variant_obj,
                    image=img
                )

        # ✅ Notifications
        # for user in User.objects.filter(is_staff=False):
        #     Notification.objects.create(
        #         user=user,
        #         message=f"New product '{product.name}' added!"
        #     )

        messages.success(request, "Product added successfully!")
        return redirect("adminpanel:product_list")

    context = {
        "categories": categories,
        "brands": brands,
        "colors": colors,
        "frame_types": frame_types,
        "frame_shapes": frame_shapes,
        "materials": materials,
    }

    return render(request, "admin/add_product.html", context)

# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from django.contrib.auth.decorators import user_passes_test
# from .models import Product, ProductVariant, ProductVariantImage, Category, SubCategory, Color, Brand, User, Notification
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
import re

@user_passes_test(lambda u: u.is_staff, login_url="adminpanel:login")
@user_passes_test(is_admin, login_url="adminpanel:login")
def edit_product(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    categories = Category.objects.all()
    brands = Brand.objects.all()
    colors = Color.objects.all()
    frame_types = FrameType.objects.all()
    frame_shapes = FrameShape.objects.all()
    materials = Material.objects.all()

    if request.method == "POST":

        # ================= BASIC =================
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.description = request.POST.get("description")

        product.brand_id = request.POST.get("brand")
        product.category_id = request.POST.get("category")
        product.subcategory_id = request.POST.get("subcategory")

        product.frame_type_id = request.POST.get("frame_type")
        product.frame_shape_id = request.POST.get("frame_shape")
        product.material_id = request.POST.get("material")

        product.save()

        # ================= VARIANT PARSE =================
        variant_data = {}

        for key, value in request.POST.items():
            match = re.match(r"variants\[(\d+)\]\[(\w+)\]", key)
            if match:
                index, field = match.groups()
                variant_data.setdefault(index, {})[field] = value

        existing_variants = {v.id: v for v in product.variants.all()}
        submitted_variant_ids = set()

        total_stock = 0

        # ================= PROCESS VARIANTS =================
        for index, data in variant_data.items():

            variant_id = data.get("id")
            color_id = data.get("color")
            stock = int(data.get("stock", 0))

            total_stock += stock

            # ===== UPDATE / CREATE VARIANT =====
            if variant_id and variant_id.isdigit() and int(variant_id) in existing_variants:
                variant = existing_variants[int(variant_id)]
                variant.color_id = color_id
                variant.stock = stock
                variant.save()
            else:
                variant = ProductVariant.objects.create(
                    product=product,
                    color_id=color_id,
                    stock=stock
                )

            submitted_variant_ids.add(variant.id)

            # ================= IMAGE HANDLING (BEST) =================

            # 🔹 1. HANDLE EXISTING IMAGES (DELETE / REPLACE BY ID)
            existing_images = request.POST.getlist(f"variants[{index}][existing_images][]")

            for img_id in existing_images:

                # ❌ DELETE CHECK
                delete_flag = request.POST.get(f"delete_image_{img_id}")
                if delete_flag == "1":
                    ProductVariantImage.objects.filter(id=img_id).delete()
                    continue

                # 🔄 REPLACE CHECK (PER IMAGE)
                new_img = request.FILES.get(f"replace_image_{img_id}")
                if new_img:
                    obj = ProductVariantImage.objects.filter(id=img_id).first()
                    if obj:
                        obj.image = new_img
                        obj.save()

            # 🔹 2. ADD NEW IMAGES
            new_images = request.FILES.getlist(f"variants[{index}][images][]")

            for img in new_images:
                ProductVariantImage.objects.create(
                    variant=variant,
                    image=img
                )

        # ================= DELETE REMOVED VARIANTS =================
        for vid, variant in existing_variants.items():
            if vid not in submitted_variant_ids:
                variant.delete()

        # ================= UPDATE TOTAL STOCK =================
        product.stock = total_stock
        product.save()

        messages.success(request, "Product updated successfully!")
        return redirect("adminpanel:product_list")

    # ================= GET =================
    return render(request, "admin/edit_product.html", {
        "product": product,
        "categories": categories,
        "brands": brands,
        "colors": colors,
        "frame_types": frame_types,
        "frame_shapes": frame_shapes,
        "materials": materials,
    })

@user_passes_test(is_admin, login_url="adminpanel:login")
def delete_product(request, id):
    Product.objects.filter(id=id).delete()
    messages.error(request, "Product deleted")
    return redirect("adminpanel:product_list")

# =====================================================
# 📦 ORDERS
# =====================================================

LOW_STOCK_THRESHOLD = 50
# adminpanel/views.py


def orders_list(request):
    orders = Order.objects.all().prefetch_related('items')
    delivery_boys = DeliveryPerson.objects.all()

    for order in orders:
        total = 0

        for item in order.items.all():
            # ❌ skip cancelled items
            if item.status and item.status.strip().lower() == "cancelled":
                continue

            total += item.total_price

        order.calculated_total = total

        # ✅ delivery logic
        order.delivery_charge = 0 if total >= 999 else 50

        order.final_total = total + order.delivery_charge

    return render(request, 'admin/orders_list.html', {
        'orders': orders,
        'delivery_boys': delivery_boys
    })
from django.shortcuts import render, get_object_or_404
from .models import Order

def order_detail(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), id=order_id)
    return render(request, "admin/order_detail.html", {"order": order})


@user_passes_test(is_admin, login_url="adminpanel:login")
def update_order_status(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get("status")
        if new_status:
            order.status = new_status
            order.save()
    return redirect("adminpanel:orders_list")


# =====================================================
# 📦 LENS
# =====================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import Lens


@user_passes_test(is_admin, login_url="adminpanel:login")
def lens_list(request):
    lenses = Lens.objects.all()
    return render(request, "admin/lens_list.html", {"lenses": lenses})


# ADD LENS
@user_passes_test(is_admin, login_url="adminpanel:login")
def add_lens(request):

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price") or 0

        power_required = request.POST.get("power_required") == "on"
        is_active = request.POST.get("is_active") == "on"

        Lens.objects.create(
            name=name,
            description=description,
            additional_price=price,
            power_required=power_required,
            is_active=is_active
        )
        messages.success(request, "Lens added successfully!")
        return redirect("adminpanel:lens_list")

    return render(request, "admin/add_lens.html")


# UPDATE LENS
@user_passes_test(is_admin, login_url="adminpanel:login")
def edit_lens(request, pk):

    lens = get_object_or_404(Lens, id=pk)

    if request.method == "POST":
        lens.name = request.POST.get("name")
        lens.description = request.POST.get("description")
        lens.additional_price = request.POST.get("price") or 0

        lens.power_required = request.POST.get("power_required") == "on"
        lens.is_active = request.POST.get("is_active") == "on"

        lens.save()
        messages.success(request, "Lens updated successfully!")
        return redirect("adminpanel:lens_list")

    return render(request, "admin/edit_lens.html", {"lens": lens})


# DELETE LENS
@user_passes_test(is_admin, login_url="adminpanel:login")
def delete_lens(request, pk):

    lens = get_object_or_404(Lens, id=pk)
    lens.delete()
    messages.error(request, "Product deleted")
    return redirect("adminpanel:lens_list")

# =====================================================
# 🏢 COMPANY INFO
# =====================================================

@user_passes_test(is_admin, login_url="adminpanel:login")
def company_create(request):
    if CompanyInfo.objects.exists():
        return redirect("adminpanel:company_update")
    if request.method == "POST":
        CompanyInfo.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            address=request.POST.get("address"),
            gst_number=request.POST.get("gst_number"),
            logo=request.FILES.get("logo"),
        )
        messages.success(request, "Company info added")
        return redirect("adminpanel:dashboard")
    return render(request, "admin/company_add.html")


@user_passes_test(is_admin, login_url="adminpanel:login")
def company_update(request):
    company = get_object_or_404(CompanyInfo)
    if request.method == "POST":
        company.name = request.POST.get("name")
        company.email = request.POST.get("email")
        company.phone = request.POST.get("phone")
        company.address = request.POST.get("address")
        company.gst_number = request.POST.get("gst_number")
        if request.FILES.get("logo"):
            company.logo = request.FILES.get("logo")
        company.save()
        messages.success(request, "Company info updated")
        return redirect("adminpanel:dashboard")
    return render(request, "admin/company_edit.html", {"company": company})


# =====================================================
# 👤 USERS
# =====================================================

@user_passes_test(is_admin, login_url="adminpanel:login")
def user_list(request):
    users = User.objects.all().order_by("-id")
    return render(request, "admin/user_list.html", {"users": users})


@user_passes_test(is_admin, login_url="adminpanel:login")
def low_stock_products(request):

    low_stock_variants = ProductVariant.objects.filter(
        stock__lte=LOW_STOCK_THRESHOLD
    ).select_related("product", "color")

    labels = [
        f"{v.product.name} - {v.color.name}"
        for v in low_stock_variants
    ]

    data = [v.stock for v in low_stock_variants]

    return render(request, "admin/low_stock_products.html", {
        "low_stock_variants": low_stock_variants,
        "labels": labels,
        "data": data,
        "low_stock_threshold": LOW_STOCK_THRESHOLD
    })


# =====================================================
# 💰 REVENUE
# =====================================================
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncMonth
from decimal import Decimal

@user_passes_test(is_admin, login_url="adminpanel:login")

def revenue_dashboard(request):
    monthly_revenue = (
        OrderItem.objects
        .filter(
            status="delivered",
            return_status__in=["none", "rejected"],
            refund_status="none"
        )
        .annotate(month=TruncMonth('order__created_at'))
        .values('month')
        .annotate(
            total=Sum(
                ExpressionWrapper(
                    F("quantity") * F("price"),
                    output_field=DecimalField()
                )
            )
        )
        .order_by('month')
    )

    revenue_months = [r['month'].strftime('%b %Y') for r in monthly_revenue if r['total']]
    revenue_values = [float(r['total']) for r in monthly_revenue if r['total']]

    return render(request, 'admin/revenue_dashboard.html', {
        'monthly_revenue': monthly_revenue,
        'revenue_months': revenue_months,
        'revenue_values': revenue_values,
    })
# =====================================================
# 🎯 OFFERS
# =====================================================

@user_passes_test(is_admin, login_url="adminpanel:login")
def create_offer(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    if request.method == "POST":
        name = request.POST.get('name')
        discount_type = request.POST.get('discount_type')
        discount_value = request.POST.get('discount_value')
        product_id = request.POST.get('product')
        category_id = request.POST.get('category')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        is_active = request.POST.get('is_active') == 'on'

        if product_id and category_id:
            messages.error(request, "Select either Product OR Category.")
            return redirect('adminpanel:create_offer')

        if not product_id and not category_id:
            messages.error(request, "Select at least Product or Category.")
            return redirect('adminpanel:create_offer')

        # ✅ SAVE OFFER FIRST
        offer = Offer.objects.create(
            name=name,
            discount_type=discount_type,
            discount_value=discount_value,
            product_id=product_id or None,
            category_id=category_id or None,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active,
        )
        if offer.discount_type == "percent":
            msg = f"{offer.discount_value}% OFF on {offer.name}"
        else:
            msg = f"Flat ₹{offer.discount_value} OFF on {offer.name}"
        # ✅ SEND NOTIFICATIONS
        for user in User.objects.filter(is_staff=False):
            Notification.objects.create(
                user=user,
                title="🔥 New Offer Available!",
                message=msg
            )

        messages.success(request, "Offer created successfully!")
        return redirect('adminpanel:offer_list')

    return render(request, 'admin/create_offer.html', {
        'products': products,
        'categories': categories
    })

@user_passes_test(is_admin, login_url="adminpanel:login")
def offer_list(request):
    offers = Offer.objects.all().order_by('-id')
    return render(request, 'admin/offer_list.html', {'offers': offers})


@user_passes_test(is_admin, login_url="adminpanel:login")
def edit_offer(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    products = Product.objects.all()
    categories = Category.objects.all()

    if request.method == "POST":
        offer.name = request.POST.get('name')
        offer.discount_type = request.POST.get('discount_type')
        offer.discount_value = request.POST.get('discount_value')
        product_id = request.POST.get('product')
        category_id = request.POST.get('category')
        offer.start_date = request.POST.get('start_date')
        offer.end_date = request.POST.get('end_date')
        offer.is_active = request.POST.get('is_active') == 'on'

        if product_id and category_id:
            messages.error(request, "Select either Product OR Category.")
            return redirect('adminpanel:edit_offer', pk=pk)

        if not product_id and not category_id:
            messages.error(request, "Select at least Product or Category.")
            return redirect('adminpanel:edit_offer', pk=pk)

        offer.product_id = product_id or None
        offer.category_id = category_id or None
        offer.save()
        if offer.discount_type == "percent":
            msg = f"{offer.discount_value}% OFF on {offer.name}"
        else:
            msg = f"Flat ₹{offer.discount_value} OFF on {offer.name}"
        # ✅ SEND NOTIFICATIONS
        for user in User.objects.filter(is_staff=False):
            Notification.objects.create(
                user=user,
                title="🔥 Updated Offer!",
                message=msg
            )


        messages.success(request, "Offer updated successfully!")
        return redirect('adminpanel:offer_list')

    return render(request, 'admin/edit_offer.html', {
        'offer': offer,
        'products': products,
        'categories': categories
    })


@user_passes_test(is_admin, login_url="adminpanel:login")
def delete_offer(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    offer.delete()
    messages.success(request, "Offer deleted successfully!")
    return redirect('adminpanel:offer_list')


# =====================================================
# 🚚 DELIVERY PERSON
# =====================================================

@user_passes_test(is_admin, login_url="adminpanel:login")
def delivery_person_list(request):
    delivery_persons = DeliveryPerson.objects.select_related('user')
    return render(request, 'admin/delivery_person_list.html', {
        'delivery_persons': delivery_persons
    })


@user_passes_test(is_admin, login_url="adminpanel:login")
def add_delivery_person(request):
    today = date.today()
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        phone = request.POST.get("phone", "").strip()
        today = date.today()
        # Validate empty fields
        if not username or not password:
            messages.error(request, "Username and Password are required.")
            return redirect("adminpanel:delivery_person_add")

        # Check duplicate username
        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("adminpanel:delivery_person_add")

        # Create User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.is_staff = True
        user.save()

        
        # ✅ joining date auto set
        DeliveryPerson.objects.create(
            user=user,
            phone=phone,
            joining_date=timezone.now().date()
        )

        messages.success(request, "Delivery person added successfully.")
        return redirect("adminpanel:delivery_person_list")
    context = {
        'today_date': today.isoformat()  # formats as YYYY-MM-DD
    }
    return render(request, "admin/add_delivery_person.html", context)
# =====================================================
# 🚚 ASSIGN ORDERS

from delivery.models import DeliveryPerson

@user_passes_test(is_admin, login_url="adminpanel:login")
def assign_delivery(request, order_id):

    if request.method == "POST":

        order = get_object_or_404(Order, id=order_id)

        # 🚫 Delivered / Cancelled block
        if order.status in ["delivered", "cancelled"]:
            messages.error(request, "Cannot change delivery person at this stage.")
            return redirect("adminpanel:orders_list")

        # 🚫 Already assigned and NOT rejected
        if order.delivery_person and order.status != "rejected":
            messages.error(request, "Order already assigned. Wait for rejection.")
            return redirect("adminpanel:orders_list")

        dp_id = request.POST.get("delivery_person")

        if not dp_id:
            messages.error(request, "Please select delivery person.")
            return redirect("adminpanel:orders_list")

        dp = get_object_or_404(DeliveryPerson, id=dp_id)

        # 🚫 Same rejected boy ne fari assign na thay
        if order.status == "rejected" and order.last_rejected_by == dp:
            messages.error(request, "This delivery person already rejected this order.")
            return redirect("adminpanel:orders_list")

        # ✅ Assign delivery
        order.delivery_person = dp
        order.status = "assigned"
        order.save()

        # 🔔 Notification create
        Notification.objects.create(
            user=dp.user,
            message=f"🚚 New Order #{order.id} assigned to you"
        )

        messages.success(request, "Delivery person assigned successfully.")

    return redirect("adminpanel:orders_list")



from adminpanel.models import OrderItem

def complete_refund(request, item_id):

    item = get_object_or_404(OrderItem, id=item_id)

    item.refund_status = "completed"
    item.save()

    return redirect("adminpanel:orders_list")
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST



@require_POST
@login_required
def approve_return(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)

    item.return_status = "approved"
    item.refund_status = "initiated"
    item.save()

    messages.success(request, "Return approved and refund initiated.")

    return redirect("adminpanel:orders_list")


@require_POST
@login_required
def reject_return(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)

    item.return_status = "rejected"
    item.save()

    messages.error(request, "Return request rejected.")

    return redirect("adminpanel:orders_list")



from adminpanel.models import OrderItem, Complaint

@login_required
def add_complaint(request, item_id):

    item = get_object_or_404(OrderItem, id=item_id)

    if request.method == "POST":

        reason = request.POST.get("reason")
        description = request.POST.get("description")

        Complaint.objects.create(
            order_item=item,
            user=request.user,
            reason=reason,
            description=description
        )

        return redirect("app:order_history")

    return render(request, "app/add_complaint.html", {"item": item})


from .models import Complaint


def complaints_list(request):

    complaints = Complaint.objects.select_related(
        "order_item",
        "user"
    ).order_by("-created_at")

    context = {
        "complaints": complaints
    }

    return render(request, "admin/complaints_list.html", context)


def resolve_complaint(request, id):

    complaint = Complaint.objects.get(id=id)
    complaint.status = "resolved"
    complaint.save()

    return redirect("adminpanel:complaints_list")


def reject_complaint(request, id):

    complaint = Complaint.objects.get(id=id)
    complaint.status = "rejected"
    complaint.save()

    return redirect("adminpanel:complaints_list")

from adminpanel.models import Complaint
from django.shortcuts import render, get_object_or_404

def complaint_detail(request, id):
    complaint = get_object_or_404(Complaint, id=id)

    context = {
        "complaint": complaint
    }

    return render(request, "admin/complaint_detail.html", context)

def review_list(request):
    reviews = Review.objects.select_related("product", "user").order_by("-created_at")

    return render(request, "admin/review_list.html", {
        "reviews": reviews
    })

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db.models import Sum, F, Q
from .models import (
    Purchase, Order, Dealer, CompanyInfo,
    PurchaseReturn, Offer, Complaint, ProductVariant, OrderItem,
)
from delivery.models import DeliveryPerson
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

User = get_user_model()


def reports(request):
    report_type = request.GET.get("type")
    dealer_id = request.GET.get("dealer")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    download = request.GET.get("download")

    data = []

    # ---------------- REPORT DATA ----------------
    if report_type == "purchase":
        data = Purchase.objects.all()
        if dealer_id:
            data = data.filter(dealer_id=dealer_id)
        if from_date and to_date:
            data = data.filter(purchase_date__range=[from_date, to_date])

    elif report_type == "sales":
        data = Order.objects.filter(status="delivered")
        if from_date and to_date:
            data = data.filter(created_at__date__range=[from_date, to_date])

    elif report_type == "cancel":
        data = Order.objects.filter(status="cancelled")

    elif report_type == "return_order":
        data = OrderItem.objects.filter(return_status__in=["requested", "approved", "completed"])
        if from_date and to_date:
            data = data.filter(order__created_at__date__range=[from_date, to_date])

    elif report_type == "users":
        data = User.objects.all()

    elif report_type == "dealer":
        data = Dealer.objects.all()

    elif report_type == "purchase_return":
        data = PurchaseReturn.objects.all()
        if from_date and to_date:
            data = data.filter(return_date__date__range=[from_date, to_date])

    elif report_type == "offer":
        data = Offer.objects.all()

    elif report_type == "complaint":
        data = Complaint.objects.all()

    elif report_type == "low_stock":
        data = ProductVariant.objects.filter(stock__lte=LOW_STOCK_THRESHOLD)

    elif report_type == "top_products":
        data = OrderItem.objects.values('product__name').annotate(total_qty=Sum('quantity')).order_by('-total_qty')[:10]

    elif report_type == "dealer_sales":
        data = Order.objects.filter(status="delivered")
        if from_date and to_date:
            data = data.filter(created_at__date__range=[from_date, to_date])
        data = data.values('delivery_person__user__username').annotate(total_sales=Sum('total_amount'))

    elif report_type == "revenue":
        orders = Order.objects.filter(status="delivered")
        if from_date and to_date:
            orders = orders.filter(created_at__date__range=[from_date, to_date])
        total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        data = [{"total_revenue": total_revenue}]

    elif report_type == "pending_orders":
        data = Order.objects.exclude(status__in=["delivered","cancelled"])

    elif report_type == "product_performance":
        data = OrderItem.objects.values('product__name').annotate(
            sold_qty=Sum('quantity'),
            returned_qty=Sum('quantity', filter=Q(return_status__in=["requested","approved","completed"]))
        )
    elif report_type == "delivery_person":
        # Get delivery persons with assigned order count
        data = DeliveryPerson.objects.annotate(
        assigned_orders=Count('orders')  # 'orders' is related_name from Order model
    )

    elif report_type == "complaint_analysis":
        data = Complaint.objects.values('status').annotate(count=Sum('id'))

    # ---------------- PDF DOWNLOAD ----------------
    if download == "pdf":
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="optiview_{report_type}_report.pdf"'
        pdf = SimpleDocTemplate(response, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Company info
        company = CompanyInfo.objects.first()
        if company:
            company_data = [
                [company.name],
                [company.address],
                [f"Phone: {company.phone} | Email: {company.email}"]
            ]
        else:
            company_data = [["Company Information Not Added"]]

        company_box = Table(company_data, colWidths=[450])
        company_box.setStyle(TableStyle([
            ("BOX",(0,0),(-1,-1),1,colors.black),
            ("BACKGROUND",(0,0),(-1,0),colors.lightblue),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,0),16),
            ("BOTTOMPADDING",(0,0),(-1,0),10)
        ]))
        elements.append(company_box)
        elements.append(Spacer(1, 20))

        # Title
        center_style = ParagraphStyle("CenterStyle", parent=styles["Heading2"], alignment=TA_CENTER)
        title = Paragraph(f"<b>{report_type.replace('_',' ').upper()} REPORT</b>", center_style)
        elements.append(title)

        # Date range centered
        date_style = ParagraphStyle("DateStyle", parent=styles["Normal"], alignment=TA_CENTER)
        if from_date and to_date:
            date_text = f"Date Range: {from_date} to {to_date}"
        else:
            date_text = "Date Range: All Dates"
        elements.append(Paragraph(date_text, date_style))
        elements.append(Spacer(1, 20))

        # Table data
        table_data = []

        if report_type == "purchase":
            table_data.append(["Bill No","Dealer","Total Amount","Date"])
            for item in data:
                table_data.append([item.bill_number, item.dealer.name, item.total_amount, str(item.purchase_date)])

        elif report_type in ["sales","cancel","pending_orders"]:
            table_data.append(["Order No","User","Total Amount","Status","Date"])
            for item in data:
                table_data.append([item.order_number, item.user.username, item.total_amount, getattr(item,'status','N/A'), str(item.created_at.date())])


        elif report_type == "return_order":
            table_data.append(["Order No", "Product", "Variant", "Qty", "User", "Date"])
    
            wrap_style = ParagraphStyle('wrap', alignment=TA_LEFT, fontSize=10)
    
            for item in data:
                # Convert color object to string
                if item.variant and item.variant.color:
                    # If you just want the name of the color
                    color_text = str(item.variant.color)  # or item.variant.color.name if it has a name attribute
                else:
                    color_text = "N/A"
        
            table_data.append([
            item.order.order_number,
            Paragraph(item.product.name, wrap_style),
            Paragraph(color_text, wrap_style),
            item.quantity,
            item.order.user.get_full_name() or item.order.user.username,
            str(item.order.created_at.date())
        ])
        elif report_type == "purchase_return":
            table_data.append(["Return ID","Dealer","Product","Qty","Date"])
            for item in data:
                table_data.append([item.id, item.purchase_item.purchase.dealer.name,
                                   item.purchase_item.variant.product.name,
                                   item.quantity, str(item.return_date.date())])

        elif report_type == "low_stock":
            table_data.append(["Product","Variant","Stock"])
            for item in data:
                table_data.append([item.product.name, item.color.name if item.color else "N/A", item.stock])

        elif report_type == "complaint":
            table_data.append(["ID","User","Reason","Description","Status","Date"])
            for item in data:
                table_data.append([item.id, item.user.username, item.reason, item.description, item.status, str(item.created_at.date())])

        elif report_type == "users":
            table_data.append(["ID","Username","Email","Joined"])
            for item in data:
                table_data.append([item.id, item.username, item.email, str(item.date_joined.date())])

        elif report_type == "dealer":
            table_data.append(["ID","Name","Phone","Email"])
            for item in data:
                table_data.append([item.id, item.name, item.phone, item.email])

        elif report_type == "offer":
            table_data.append(["ID","Title","Discount Type","Value","Start","End"])
            for item in data:
                table_data.append([item.id, item.name, item.discount_type, item.discount_value, item.start_date, item.end_date])

        elif report_type == "top_products":
            table_data.append(["Product Name","Quantity Sold"])
            for item in data:
                table_data.append([item['product__name'],item['total_qty']])

        elif report_type == "dealer_sales":
            table_data.append(["Dealer","Total Sales"])
            for item in data:
                table_data.append([item['delivery_person__user__username'], item['total_sales']])

        elif report_type == "revenue":
            table_data.append(["Total Revenue"])
            table_data.append([f"₹{data[0]['total_revenue']}"])

        elif report_type == "product_performance":
            table_data.append(["Product","Sold Qty","Returned Qty"])
            for item in data:
                table_data.append([item['product__name'], item['sold_qty'], item.get('returned_qty',0)])

        elif report_type == "complaint_analysis":
            table_data.append(["Status","Count"])
            for item in data:
                table_data.append([item['status'], item['count']])
        elif report_type == "delivery_person":
            table_data.append(["Name","Email","Phone","Joining Date","Assigned Orders"])
            for d in data:
                table_data.append([
                d.user.get_full_name() or d.user.username,
                d.user.email,
                d.phone,
                str(d.joining_date) if d.joining_date else "N/A",
                d.assigned_orders
            ])

        if len(table_data) <= 1:
            table_data.append(["No Data Available"])

        # Set dynamic column widths for users and dealer tables to avoid overlapping email
        if report_type == "users":
            col_widths = [0.7*inch, 1.5*inch, 2.5*inch, 1.2*inch]
        elif report_type == "dealer":
            col_widths = [0.7*inch, 2*inch, 1.5*inch, 2.5*inch]
        elif report_type=='product_performance':
            col_widths=[2.5*inch,0.7*inch,1*inch]
        elif report_type=='low_stock':
            col_widths=[2.5*inch,0.7*inch,0.7*inch]
        elif report_type=='purchase_return':
            col_widths=[0.7*inch,2*inch,2.5*inch,1*inch,1*inch]
        elif report_type=='return_order':
            col_widths = [2.*inch, 2.5*inch, 0.7*inch, 0.6*inch, 1.2*inch]
        elif report_type=='delivery_person':
            col_widths = [1.5*inch, 2.5*inch, 1.5*inch, 1.5*inch, 1.2*inch]
        elif report_type=='top_products':
            col_widths=[2.5*inch,1.5*inch]
        else:
            col_widths = [1.5*inch]*len(table_data[0])

        table = Table(table_data, repeatRows=1, colWidths=col_widths)
        table.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.darkblue),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.5,colors.grey),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.whitesmoke, colors.lightgrey])
        ]))
        elements.append(table)
        elements.append(Spacer(1,20))

        # Footer centered
        footer_style = ParagraphStyle("FooterStyle", parent=styles["Italic"], alignment=TA_CENTER)
        elements.append(Paragraph("Generated by Optiview Admin Panel", footer_style))

        pdf.build(elements)
        return response

    dealers = Dealer.objects.all()
    return render(request, "admin/reports.html", {"data": data, "report_type": report_type, "dealers": dealers})