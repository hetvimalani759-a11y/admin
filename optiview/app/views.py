from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from decimal import Decimal
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from reportlab.lib import styles
from urllib3 import request
from .models import UserProfile
import json
import razorpay
from django.conf import settings
from io import BytesIO
import os
# import qrcode

from adminpanel.models import Product, Category, Notification, Order, OrderItem,DashboardImage,ProductVariant,ProductVariantImage,Color,Brand,FrameType,FrameShape,CompanyInfo,Material
from .models import Cart, Wishlist
from adminpanel.utils import is_customer

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.units import inch


# ==========================
# 🌐 PUBLIC
# ==========================
from django.http import JsonResponse

def categories_view(request):
    categories = Category.objects.all()
    return render(request, 'app/categories.html', {'categories': categories})

def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = category.product_set.all()  # default reverse name
    return render(request, 'app/category_products.html', {'category': category, 'products': products})

# def notifications_api(request):
#     if request.user.is_authenticated:
#         notifications = Notification.objects.filter(
#             user=request.user, is_read=False
#         ).order_by('-created_at')
#         data = [
#             {"text": n.text, "time": n.created_at.strftime("%Y-%m-%d %H:%M")}
#             for n in notifications
#         ]
#         return JsonResponse({"notifications": data})
#     return JsonResponse({"notifications": []})



def home(request):
    # Latest 6 products added (most recent first)
    latest_products = Product.objects.all().order_by('-created_at')[:6]
    
    # Optional: load categories if you have Category model
    categories = Category.objects.all() 
    images = DashboardImage.objects.all()
    

    return render(request, 'app/index.html', {
        'latest_products': latest_products,
        'categories': categories,
        'images': images 
    })





from django.db.models import Q
from adminpanel.models import (
    Product, Category, Color, Brand,
    FrameType, FrameShape,
)
from django.db.models import Q

def shop(request):

    # ================= BASE QUERY =================
    products = Product.objects.filter(is_active=True)
    
    # ================= FILTER DATA =================
    categories = Category.objects.filter(is_active=True)
    colors = Color.objects.all()
    brands = Brand.objects.all()
    frame_types = FrameType.objects.all()
    frame_shapes = FrameShape.objects.all()
    materials=Material.objects.all()
    genders = [
        {"id": "male", "name": "Male"},
        {"id": "female", "name": "Female"},
        {"id": "unisex", "name": "Unisex"},
    ]

    # ================= GET PARAMETERS =================
    search_query = request.GET.get("q", "").strip()

    selected_categories = request.GET.getlist("category")
    selected_subcategories = request.GET.getlist("subcategory")
    selected_colors = request.GET.getlist("color")
    selected_genders = [g.lower() for g in request.GET.getlist("gender")]
    selected_frames = request.GET.getlist("frame_type")
    selected_shapes = request.GET.getlist("frame_shape")
    selected_brands = request.GET.getlist("brand")
    selected_materials=request.GET.getlist('material')
    stock_filter = request.GET.get("stock")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    # ================= APPLY FILTERS =================

    # 🔍 SEARCH
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        )

    # 📂 Category
    if selected_categories:
        products = products.filter(category__id__in=selected_categories)

    # 📁 Subcategory
    if selected_subcategories:
        products = products.filter(subcategory__id__in=selected_subcategories)

    # 🎨 Color (via variants)
    if selected_colors:
        products = products.filter(variants__color__id__in=selected_colors)

    # 👤 Gender
    if selected_genders:
        products = products.filter(gender__in=selected_genders)

    # 🕶 Frame Type
    if selected_frames:
        products = products.filter(frame_type__id__in=selected_frames)

    # 🔷 Frame Shape
    if selected_shapes:
        products = products.filter(frame_shape__id__in=selected_shapes)
    if selected_materials:
        products = products.filter(material__id__in=selected_materials)
    # 🏷 Brand
    if selected_brands:
        products = products.filter(brand__id__in=selected_brands)

    # 📦 In Stock Only (FIXED FOR VARIANTS)
    if stock_filter == "1":
        products = products.filter(variants__stock__gt=0)

    # 💰 Price Range
    try:
        if min_price:
            products = products.filter(price__gte=float(min_price))
        if max_price:
            products = products.filter(price__lte=float(max_price))
    except ValueError:
        pass

    # Remove duplicates & sort newest first
    products = products.distinct().order_by("-created_at")

    # ================= ADD HAS_STOCK FLAG FOR TEMPLATE =================
    for product in products:
        product.has_stock = product.variants.filter(stock__gt=0).exists()

    # ================= WISHLIST =================
    wishlist_ids = []
    if request.user.is_authenticated and is_customer(request.user):
        wishlist_ids = list(
            Wishlist.objects.filter(user=request.user)
            .values_list("product_id", flat=True)
        )

    # ================= CONTEXT =================
    context = {
        "products": products,
        "categories": categories,
        "colors": colors,
        "brands": brands,
        "frame_types": frame_types,
        "frame_shapes": frame_shapes,
        'materials':materials,
        "genders": genders,

        "search_query": search_query,
        "selected_categories": selected_categories,
        "selected_subcategories": selected_subcategories,
        "selected_colors": selected_colors,
        "selected_genders": selected_genders,
        "selected_frames": selected_frames,
        "selected_shapes": selected_shapes,
        "selected_brands": selected_brands,
        'selected_materials':selected_materials,
        "min_price": min_price,
        "max_price": max_price,
        "wishlist_ids": wishlist_ids,
    }

    return render(request, "app/shop.html", context)

def about(request):
    return render(request, "app/about.html")

def contact(request):
    company = CompanyInfo.objects.first()   # get saved company info

    return render(request, "app/contact.html", {
        "company": company
    })


# ==========================
# 🔐 AUTH (Customer Panel)
# ==========================
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction, IntegrityError
from .models import UserProfile
import re

def register_view(request):
    

    if request.method == "POST":
       
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        phone = request.POST.get("phone", "").strip()
        dob = request.POST.get("dob") or None
        gender = request.POST.get("gender")
        address = request.POST.get("address", "").strip()


        # ---------- DOB VALIDATION ----------
        if dob:
            try:
                dob_date = date.fromisoformat(dob)

                if dob_date > date.today():
                    messages.error(request, "Date of birth cannot be in the future!")
                    return render(request, "app/register.html", request.POST)

            except ValueError:
                    messages.error(request, "Invalid date format!")
                    return render(request, "app/register.html", request.POST)
        # ---------- REQUIRED FIELD CHECK ----------
        if not username or not email or not password or not password2 or not gender:
            messages.error(request, "Please fill all required fields!")
            return render(request, "app/register.html", request.POST)

        # ---------- PASSWORD MATCH ----------
        if password != password2:
            messages.error(request, "Passwords do not match!")
            return render(request, "app/register.html", request.POST)

        # ---------- EMAIL VALIDATION ----------
        email_regex = r"[^@]+@[^@]+\.[^@]+"
        if not re.match(email_regex, email):
            messages.error(request, "Invalid email format!")
            return render(request, "app/register.html", request.POST)

        # ---------- UNIQUE CHECKS ----------
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, "app/register.html", request.POST)
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, "app/register.html", request.POST)

        # ---------- CREATE USER AND PROFILE ATOMICALLY ----------
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    
                )

                UserProfile.objects.create(
                    user=user,
                    phone=phone if phone else None,
                    dob=dob if dob else None,
                    gender=gender,
                    address=address if address else None
                )

            messages.success(request, "Account created successfully! Please login.")
            return redirect("app:login")

        except IntegrityError:
            messages.error(request, "Something went wrong. Please try again.")
            return render(request, "app/register.html", request.POST)

    # GET request
    return render(request, "app/register.html")
 # assuming you have this function

def login_view(request):
    # Redirect already logged-in customers
    if request.user.is_authenticated and is_customer(request.user):
        return redirect("app:home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user and is_customer(user):
            # Login user
            auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            
            # Optional: expire session on browser close
            request.session.set_expiry(0)
            request.session.cycle_key()  # prevent session fixation
            request.session.save()

            # Set separate cookie for customer panel
            response = redirect("app:home")
            response.set_cookie("customer_sessionid", request.session.session_key)
            return response

        # Invalid login
        messages.error(request, "Invalid credentials or not a customer account.")
        return redirect("app:login")

    # GET request
    return render(request, "app/login.html")
@login_required
@user_passes_test(is_customer, login_url="app:login")
def customer_logout(request):
    auth_logout(request)
    response = redirect("app:home")
    response.delete_cookie("customer_sessionid")
    return response

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, "app/profile.html", {"profile": profile})


from django.http import JsonResponse
from .models import PincodeMapping

from django.http import JsonResponse
from .models import PincodeMapping

def get_pincode(request):
    area = request.GET.get('area', '').strip()
    city = request.GET.get('city', '').strip()
    state = request.GET.get('state', '').strip()

    mapping = PincodeMapping.objects.filter(
        area__icontains=area,
        city__iexact=city,
        state__iexact=state
    ).first()

    if mapping:
        return JsonResponse({'pincode': mapping.pincode})
    
    return JsonResponse({'pincode': None})
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from datetime import date


@login_required
def edit_profile(request):
    profile = getattr(request.user, "profile", None)

    if request.method == 'POST':
        user = request.user
        new_username = request.POST.get('username', '').strip()

        # ===== USERNAME VALIDATION =====
        if not new_username:
            messages.error(request, "Username cannot be empty")
            return render(request, 'app/edit_profile.html', {
                'profile': profile,
                'today': date.today()
            })

        if User.objects.filter(username=new_username).exclude(id=user.id).exists():
            messages.error(request, "Username already taken")
            return render(request, 'app/edit_profile.html', {
                'profile': profile,
                'today': date.today()
            })

        # ===== DOB VALIDATION =====
        dob = request.POST.get('dob')

        if dob:
            dob_date = date.fromisoformat(dob)

            if dob_date > date.today():
                messages.error(request, "Date of birth cannot be in the future")
                return render(request, 'app/edit_profile.html', {
                'profile': profile,
                'today': date.today()
            })

        # ✅ SAVE DOB (THIS WAS MISSING)
        profile.dob = dob_date
        # ===== SAVE USER =====
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.username = new_username
        user.email = request.POST.get('email', '').strip()
        user.save()

        update_session_auth_hash(request, user)

        # ===== PROFILE =====
        if profile:
            profile.phone = request.POST.get('phone', '').strip()
            profile.gender = request.POST.get('gender', '').strip()
            profile.address = request.POST.get('address', '').strip()
            profile.area = request.POST.get('area', '').strip()
            profile.city = request.POST.get('city', '').strip()
            profile.state = request.POST.get('state', '').strip()

            # PINCODE AUTO
            if profile.area and profile.city:
                mapping = PincodeMapping.objects.filter(
                    area__iexact=profile.area.strip(),
                    city__iexact=profile.city.strip()
                ).first()

                if mapping:
                    profile.pincode = mapping.pincode

            # IMAGE
            if 'profile_image' in request.FILES:
                profile.profile_image = request.FILES['profile_image']

            profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('app:profile')

    return render(request, 'app/edit_profile.html', {
        'profile': profile,
        'today': date.today()
    })
    
from django.http import JsonResponse
from .models import PincodeMapping

def get_location_by_pincode(request):
    pincode = request.GET.get('pincode')
    if not pincode:
        return JsonResponse({'error': 'Pincode required'}, status=400)

    try:
        mapping = PincodeMapping.objects.get(pincode=pincode)
        return JsonResponse({
            'city': mapping.city,
            'area': mapping.area
        })
    except PincodeMapping.DoesNotExist:
        return JsonResponse({'error': 'Pincode not found'}, status=404)

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, update_session_auth_hash
from django.shortcuts import render, redirect

@login_required
def change_password(request):
    error = None
    success = None

    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = request.user

        # 1️⃣ Check current password
        if not user.check_password(current_password):
            error = "Current password is incorrect."

        # 2️⃣ Check new password match
        elif new_password != confirm_password:
            error = "New password and confirm password do not match."

        else:
            # 3️⃣ Set new password
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # keep logged in
            success = "Password updated successfully."

    return render(request, "app/change_password.html", {"error": error, "success": success})

import random
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect

# You need a model to store OTPs temporarily
from django.utils import timezone
from datetime import date, timedelta
from adminpanel.models import OTPCode

def forgot_password(request):
    error = None
    success = None

    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            error = "No account found with this email."
            return render(request, "app/forgot_password.html", {"error": error})

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        # Save OTP to database with expiry (e.g., 5 min)
        OTPCode.objects.create(user=user, code=otp, expires_at=timezone.now() + timedelta(minutes=5))

        # Send OTP by email
        send_mail(
            subject="Your OTP for password reset",
            message=f"Your OTP code is: {otp}. It will expire in 5 minutes.",
            from_email="asitamalani@gmail.com",
            recipient_list=[email],
            fail_silently=False,
        )

        success = "OTP sent to your email. Please check your inbox."
        return redirect(f"{reverse('app:verify_otp')}?email={email}")
       

    return render(request, "app/forgot_password.html")
def verify_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        otp_input = request.POST.get("otp")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        try:
            user = User.objects.get(email=email)
            otp_record = OTPCode.objects.filter(user=user, code=otp_input, verified=False).last()
        except User.DoesNotExist:
            return render(request, "app/verify_otp.html", {"error": "Invalid email or OTP."})

        if not otp_record or otp_record.is_expired():
            return render(request, "app/verify_otp.html", {"error": "OTP expired or invalid."})

        if new_password != confirm_password:
            return render(request, "app/verify_otp.html", {"error": "Passwords do not match."})

        user.set_password(new_password)
        user.save()
        otp_record.verified = True
        otp_record.save()

        return redirect("app:login")  # password reset successful

    return render(request, "app/verify_otp.html")

# ==========================
# 🔐 CUSTOMER ONLY
# ==========================
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from adminpanel.models import Product, ProductVariant,Lens
from .models import Cart, Wishlist




def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    variants = product.variants.all()

    wishlist_ids = []
    if request.user.is_authenticated and is_customer(request.user):
        wishlist_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list("product_id", flat=True)

    reviews = product.reviews.select_related("user").all()

    # 👇 GET LENSES FROM ADMIN
    lenses = Lens.objects.filter(is_active=True)

    product.has_stock = variants.filter(stock__gt=0).exists()

    return render(request, "app/product_detail.html", {
        "product": product,
        "variants": variants,
        "wishlist_ids": wishlist_ids,
        "reviews": reviews,
        "lenses": lenses,   # 👈 SEND TO TEMPLATE
    })


# views.py
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required



@login_required
def add_to_cart(request, product_id):

    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST required"}, status=405)

    product = get_object_or_404(Product, id=product_id)

    # ---------- Parse request ----------
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        data = {}

    variant_id = data.get("variant_id")
    lens_id = data.get("lens_id")
    left_eye = data.get("left_eye")
    right_eye = data.get("right_eye")

    if not variant_id:
        return JsonResponse({"success": False, "error": "Select color/variant"})

    variant = get_object_or_404(ProductVariant, id=variant_id, product=product)

    if variant.stock <= 0:
        return JsonResponse({"success": False, "error": "Out of stock"})


    # ---------- Lens handling ----------
    lens = None
    left_power = ""
    right_power = ""

    if lens_id:
        try:
            lens = Lens.objects.get(id=lens_id, is_active=True)

            if lens.power_required:
                if not left_eye or not right_eye:
                    return JsonResponse({
                        "success": False,
                        "error": "Enter eye power"
                    })

                left_power = left_eye
                right_power = right_eye

        except Lens.DoesNotExist:
            lens = None


    # ---------- Create cart item ----------
    cart_item = Cart.objects.filter(
        user=request.user,
        product=product,
        variant=variant,
        lens=lens,
        left_eye_power=left_power,
        right_eye_power=right_power
    ).first()

    if cart_item:
        if cart_item.quantity >= variant.stock:
            return JsonResponse({"success": False, "error": "Stock limit reached"})
        cart_item.quantity += 1
        cart_item.save()
    else:
        cart_item = Cart.objects.create(
            user=request.user,
            product=product,
            variant=variant,
            lens=lens,
            quantity=1,
            left_eye_power=left_power,
            right_eye_power=right_power
        )


    

    # ---------- Cart count ----------
    cart_count = Cart.objects.filter(user=request.user).count()

    return JsonResponse({
        "success": True,
        "cart_count": cart_count
    })

@login_required
def cart_view(request):
    items = Cart.objects.filter(user=request.user)
    summary = _cart_summary(request.user)

    return render(request, "app/cart.html", {
        "items": items,
        **summary   # 🔥 THIS IS THE FIX
    })

@login_required
def cart_count(request):
    count = Cart.objects.filter(user=request.user).count()

    return JsonResponse({
    "success": True,
    "cart_count": count
})




from decimal import Decimal
from .models import Cart

def _cart_summary(user):
    items = Cart.objects.filter(user=user).select_related("product", "lens", "variant")

    original_total = Decimal("0.00")
    total = Decimal("0.00")

    for item in items:
        quantity = item.quantity

        lens_price = item.lens.additional_price if item.lens else Decimal("0.00")

        # ORIGINAL PRICE (without offer)
        original_price = Decimal(item.product.price) + lens_price

        # FINAL PRICE (with offer + lens)
        final_price = item.unit_price

        original_total += original_price * quantity
        total += final_price * quantity

    discount_total = original_total - total

    delivery_charge = Decimal("0.00") if total >= 999 else Decimal("50.00")
    grand_total = total + delivery_charge

    return {
        "items_count": items.count(),
        "original_total": int(original_total),
        "discount_total": int(discount_total),
        "delivery_charge": int(delivery_charge),
        "grand_total": int(grand_total),
        "total_saved": int(discount_total),
        "total": int(total),
    }
@login_required
@login_required
def increase_qty(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)

    # Get correct stock
    stock = item.variant.stock if item.variant else item.product.stock

    # Apply max limit rule
    max_allowed = min(stock, 5)

    if item.quantity >= max_allowed:

        if stock <= 5:
            message = f"⚠ Stock reached end. Only {stock} available."
        else:
            message = "⚠ Maximum 5 items allowed per product."

        return JsonResponse({
            "success": False,
            "message": message
        })

    item.quantity += 1
    item.save()

    return JsonResponse({
        "success": True,
        "quantity": item.quantity,
        "summary": _cart_summary(request.user)
    })
@login_required
def decrease_qty(request, item_id):
    try:
        item = get_object_or_404(Cart, id=item_id, user=request.user)

        if item.quantity <= 1:
            return JsonResponse({"success": False, "message": "Quantity cannot be less than 1."})

        item.quantity -= 1
        item.save()
        return JsonResponse({"success": True, "quantity": item.quantity, "summary": _cart_summary(request.user)})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def remove_from_cart(request, item_id):
    try:
        get_object_or_404(Cart, id=item_id, user=request.user).delete()
        return JsonResponse({"success": True, "summary": _cart_summary(request.user)})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# ==========================
# ❤️ WISHLIST
# ==========================

@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if not created:
        wishlist_item.delete()
        return JsonResponse({"status": "removed"})

    return JsonResponse({"status": "added"})


from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from .models import Product

@user_passes_test(is_customer, login_url="app:login")
def wishlist_view(request):
    products = Product.objects.filter(wishlist__user=request.user).prefetch_related('variants__images')
    
    # Create a dictionary mapping product.id -> has_stock
   
    for product in products:
        product.has_stock = product.variants.filter(stock__gt=0).exists()
    
    wishlist_ids = products.values_list("id", flat=True)

    return render(
        request,
        "app/wishlist.html",
        {
            "products": products,
            "wishlist_ids": wishlist_ids,
            
        }
    )
@user_passes_test(is_customer, login_url="app:login")
def remove_from_wishlist(request, item_id):
    get_object_or_404(Wishlist, id=item_id, user=request.user).delete()
    return redirect("app:wishlist")


# ==========================
# 🔔 NOTIFICATIONS
# ==========================



@login_required
def get_notifications(request):
    if not is_customer(request.user):
        return JsonResponse({"notifications": []})

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




@user_passes_test(is_customer, login_url="app:login")
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, id=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({"success": True})


# ==========================
# 💳 RAZORPAY
# ==========================

@csrf_exempt
@user_passes_test(is_customer, login_url="app:login")
def create_order(request):
    if request.method == "POST":
        data = json.loads(request.body)
        amount = int(float(data.get("amount")))

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order = client.order.create({"amount": amount * 100, "currency": "INR", "payment_capture": 1})

        return JsonResponse({"order_id": order["id"], "key": settings.RAZORPAY_KEY_ID, "amount": amount})


# ==========================
# 💳 CHECKOUT
# ==========================




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from decimal import Decimal
from .models import Cart
from adminpanel.models import Order, OrderItem
from django.http import JsonResponse

# Demo pincode → address mapping
PINCODE_DATA = {
    "380001": {"address": "Paldi, Ellis Bridge", "city": "Ahmedabad", "state": "Gujarat"},
    "110001": {"address": "Connaught Place", "city": "New Delhi", "state": "Delhi"},
    # add more as needed
}

@login_required
def get_full_address_by_pincode(request, pincode):
    info = PINCODE_DATA.get(pincode)
    if info:
        return JsonResponse({"success": True, **info})
    return JsonResponse({"success": False})

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from adminpanel.models import Notification

@login_required
def mark_notification_read(request, notif_id):
    try:
        notif = Notification.objects.get(id=notif_id, user=request.user)
        notif.is_read = True
        notif.save()
        return JsonResponse({"status": "success"})
    except Notification.DoesNotExist:
        return JsonResponse({"status": "error"}, status=404)
    
@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False   # ✅ IMPORTANT
    ).order_by('-created_at')

    data = {
        "count": notifications.count(),
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message
            }
            for n in notifications
        ]
    }

    return JsonResponse(data)

from django.http import JsonResponse
from .models import PincodeMapping

def get_pincode(request):
    area = request.GET.get('area')
    city = request.GET.get('city')
    state = request.GET.get('state')

    mapping = PincodeMapping.objects.filter(
        area__iexact=area,
        city__iexact=city,
        state__iexact=state
    ).first()

    if mapping:
        return JsonResponse({'pincode': mapping.pincode})
    
    return JsonResponse({'pincode': None})



from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from .models import Cart
from adminpanel.models import Order, OrderItem


@login_required
@transaction.atomic
def checkout(request):

    user = request.user
    user_profile = getattr(user, "profile", None)

    cart_items = Cart.objects.filter(user=user).select_related(
        "product", "variant", "lens"
    )

    if not cart_items.exists():
        return redirect("app:cart")

    # ================= CART SUMMARY =================
    summary = _cart_summary(user)
    subtotal = Decimal(summary["total"])
    delivery_charge = Decimal(summary["delivery_charge"])
    grand_total = Decimal(summary["grand_total"])

    # ================= POST =================
    if request.method == "POST":

        payment_method = request.POST.get("payment")
        payment_method = request.POST.get("payment")

        # ✅ VALIDATION
        if not payment_method:
            return HttpResponse("Please select payment method")
        # ===== COD LIMIT =====
        if payment_method == "COD" and subtotal > 2000:
            return HttpResponse("❌ COD not allowed above ₹2000. Please choose Online Payment.")

        # ===== CREATE ORDER =====
        order = Order.objects.create(
            user=user,
            full_name=request.POST.get("full_name"),
            phone=request.POST.get("phone"),
            address=request.POST.get("address"),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
            pincode=request.POST.get("pincode"),
            payment_method=payment_method,
            total_amount=grand_total
        )

        # ===== PROCESS CART ITEMS =====
        for item in cart_items:

            product = item.product
            variant = item.variant
            qty = item.quantity
            price = item.unit_price

            # ===== STOCK CHECK =====
            if variant and qty > variant.stock:
                return HttpResponse(
                    f"{product.name} ({variant.color.name}) out of stock"
                )

            # ===== REDUCE STOCK =====
            if variant:
                variant.stock -= qty
                variant.save()

            # ===== CREATE ORDER ITEM =====
            OrderItem.objects.create(
                order=order,
                product=product,
                variant=variant,
                quantity=qty,
                price=price,
                lens=item.lens,
                lens_type=item.lens.name if item.lens else None,
                left_eye_power=item.left_eye_power or None,
                right_eye_power=item.right_eye_power or None,
                status="pending"
            )

        # ===== PAYMENT =====
        if payment_method == "ONLINE":
            if request.POST.get("razorpay_payment_id"):
                order.payment_status = True
            else:
                return HttpResponse("Payment failed")

        else:
            order.payment_status = False

        order.save()

        # ===== CLEAR CART =====
        cart_items.delete()

        return redirect("app:order_success")

    # ================= GET =================

    address_data = {}

    if user_profile:
        address_data = {
            "full_name": f"{user.first_name} {user.last_name}".strip(),
            "phone": getattr(user_profile, "phone", ""),
            "address": getattr(user_profile, "address", ""),
            "area": getattr(user_profile, "area", ""),
            "city": getattr(user_profile, "city", ""),
            "state": getattr(user_profile, "state", ""),
            "pincode": getattr(user_profile, "pincode", ""),
        }

    return render(request, "app/checkout.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "delivery": delivery_charge,
        "total": grand_total,
        "saved_amount": summary["discount_total"],
        "has_address": bool(address_data),
        "address_data": address_data,
    })
from django.http import JsonResponse

def get_cities(request):
    state = request.GET.get("state")

    data = {
    "Gujarat": [
        "Ahmedabad", "Surat", "Rajkot", "Vadodara",
        "Gandhinagar", "Bhavnagar", "Jamnagar",
        "Junagadh", "Anand", "Navsari", "Morbi"
    ],

    "Maharashtra": [
        "Mumbai", "Pune",
        "Nagpur", "Nashik", "Thane",
        "Aurangabad", "Solapur", "Kolhapur",
        "Amravati", "Navi Mumbai"
    ],

    "Delhi": [
        "New Delhi",
        "North Delhi", "South Delhi",
        "East Delhi", "West Delhi",
        "Central Delhi", "Dwarka",
        "Rohini", "Shahdara"
    ],

    

    "Rajasthan": [
        "Jaipur", "Jodhpur", "Udaipur",
        "Kota", "Ajmer", "Bikaner",
        "Alwar", "Bharatpur", "Sikar"
    ]

    }

    return JsonResponse({"cities": data.get(state, [])})
# # views.py
# from django.shortcuts import render
# from adminpanel.models import Product  # your glasses products
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from adminpanel.models import Order, OrderItem

User = get_user_model()
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from adminpanel.models import OrderItem, Review
@login_required
# app/views.py


@login_required
def add_feedback(request,item_id):  # must match URL
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)

    # if item.order.status != "delivered":
    #     return redirect("app:order_history")

    if request.method == "POST":
        rating = int(request.POST.get("rating"))
        comment = request.POST.get("comment", "")

        Review.objects.create(
            product=item.product,
            user=request.user,
            rating=rating,
            comment=comment
        )

        return redirect("app:order_history")

    return render(request, "app/add_feedback.html", {"item": item})


def virtual_tryon(request):
    products = Product.objects.all()  # get all base products
    return render(request, "app/tryon.html", {"products": products})
def virtualtryon(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    variant_images = []

    for variant in product.variants.all():
        main_image = variant.images.first()   # ✅ ONLY FIRST IMAGE

        if main_image:
            variant_images.append({
                "name": f"{product.name} - {variant.color.name if variant.color else ''}",
                "image": main_image.image.url
            })

    context = {
        "product": product,
        "variant_images": variant_images
    }

    return render(request, "app/virtual_tryon.html", context)

# ==========================
# 📦 ORDERS
# ==========================


@login_required
@user_passes_test(is_customer, login_url="app:login")
def order_history(request):

    orders = Order.objects.filter(user=request.user).prefetch_related("items")

    orders_with_timeline = []

    for order in orders:

        status = order.status.lower()

        # 🎯 TIMELINE INDEX LOGIC
        if status in ["pending", "assigned", "accepted"]:
            current_index = 0

        elif status == "out_for_delivery":
            current_index = 1

        elif status == "delivered":
            current_index = 2

        else:  # cancelled or unknown
            current_index = 0

        timeline_steps = ["Placed", "Shipped", "Delivered"]

        timeline = []
        for i, step in enumerate(timeline_steps):
            timeline.append({
                "status": step,
                "active": i <= current_index
            })

        orders_with_timeline.append({
            "order": order,
            "timeline": timeline
        })

    return render(request, "app/order_history.html", {
        "orders": orders_with_timeline
    })



@user_passes_test(is_customer, login_url="app:login")
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all()
    return render(request, "app/order_detail.html", {"order": order, "items": items})


@user_passes_test(is_customer, login_url="app:login")
def order_success(request):
    return render(request, "app/order_success.html")

from django.views.decorators.http import require_POST
from django.contrib import messages

@require_POST
@login_required
def cancel_order_item(request, item_id):

    item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user
    )

    # ❌ Cannot cancel
    if item.status in ["out_for_delivery", "delivered"]:
        messages.error(request, "Item already out for delivery. Cannot cancel.")
        return redirect("app:order_history")

    if item.status == "cancelled":
        messages.warning(request, "Item already cancelled.")
        return redirect("app:order_history")

    # ✅ Get quantity
    try:
        qty = int(request.POST.get("quantity", 1))
    except:
        qty = 1

    # ❗ STRICT VALIDATION
    if qty <= 0:
        messages.error(request, "Invalid quantity")
        return redirect("app:order_history")

    if qty > item.quantity:
        messages.error(request, "You cannot cancel more than available quantity.")
        return redirect("app:order_history")

    # ✅ Reduce quantity
    item.quantity -= qty

    # 💰 REFUND LOGIC
    if item.order.payment_method.upper() == "ONLINE":
        refund_amount = item.price * qty
        messages.success(request, f"₹{refund_amount} refund initiated")

        # Full cancel → mark refund
        if item.quantity == 0:
            item.refund_status = "initiated"

    else:
        # Only show cancel message for COD
        messages.success(request, f"{qty} item(s) cancelled")

    # ✅ If fully cancelled
    if item.quantity == 0:
        item.status = "cancelled"

    item.save()

    # ✅ Restore stock
    if item.variant:
        item.variant.stock += qty
        item.variant.save()

    # 🔥 Update parent order
    item.order.update_order_status()

    return redirect("app:order_history")
from decimal import Decimal
from io import BytesIO
import os
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont


@login_required
@user_passes_test(is_customer, login_url="app:login")
@login_required
@user_passes_test(is_customer, login_url="app:login")
@login_required
def order_invoice(request, order_id):


    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = list(order.items.select_related("product"))

# ================= VALIDATION =================

    # ✅ Keep only valid items (ONLY delivered & not returned)
    valid_items = [
    item for item in items
    if item.status != "cancelled"
    
    and item.quantity > 0   # 🔥 IMPORTANT FIX
]

# ❌ BLOCK only if ALL items invalid
    if len(valid_items) == 0:
        messages.error(request, "Invoice not available because all items are cancelled or returned.")
        return redirect("app:order_history")
# ================= PDF SETUP =================

    # ================= PDF SETUP =================



    # ✅ 1. Create styles FIRST
    styles = getSampleStyleSheet()

# ✅ 2. Register Arial font
    font_path = "C:/Windows/Fonts/arial.ttf"
    pdfmetrics.registerFont(TTFont("CustomFont", font_path))

# ✅ 3. Apply font
    styles["Normal"].fontName = "CustomFont"
    styles["Title"].fontName = "CustomFont"

    buffer = BytesIO()
    doc = SimpleDocTemplate(
    buffer,
    pagesize=A4,
    rightMargin=36,
    leftMargin=36,
    topMargin=36
    )

    elements = []

# ================= HEADER =================

    

    logo_path = os.path.join(settings.BASE_DIR, "static", "images", "logo.png")

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=110, height=45)
    else:
        logo = Paragraph("<b>Optiview</b>", styles["Title"])

    company_info = Paragraph("""
    <b>Optiview Pvt Ltd</b><br/>
    Premium Optical Store<br/>
    support@optiview.com<br/>
    +91 98765 43210
    """, styles["Normal"])

    header_table = Table(
    [[logo, company_info]],
    colWidths=[2.5 * inch, 3.5 * inch]
    )

    header_table.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
]))

    elements.append(header_table)
    elements.append(Spacer(1, 20))

# ================= TITLE =================

    title_style = ParagraphStyle(
    "TitleStyle",
    fontName="CustomFont",
    fontSize=22,
    alignment=1,
    spaceAfter=16
)

    elements.append(Paragraph("INVOICE", title_style))

# ================= CUSTOMER DETAILS =================

    left = Paragraph(f"""
    <b>Bill To:</b><br/>
    {order.full_name}<br/>
    {order.phone}<br/>
    {order.address}<br/>
    {order.city}, {order.state} - {order.pincode}
    """, styles["Normal"])

    right = Paragraph(f"""
    <b>Invoice #:</b> {order.id}<br/>
    <b>Date:</b> {order.created_at.strftime('%d %b %Y')}<br/>
    <b>Payment:</b> {order.payment_method}<br/>
    """, styles["Normal"])

    info_table = Table(
    [[left, right]],
    colWidths=[3.5 * inch, 2.5 * inch]
)

    info_table.setStyle(TableStyle([
    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#2563eb")),
    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
    ("LEFTPADDING", (0, 0), (-1, -1), 12),
    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ("TOPPADDING", (0, 0), (-1, -1), 10),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(info_table)
    elements.append(Spacer(1, 18))

# ================= PRODUCT TABLE =================

    product_data = [["Product", "Qty", "Price", "Total"]]
    subtotal = Decimal("0.00")

    for item in valid_items:
        price = Decimal(item.price)
        qty = Decimal(item.quantity)
        total = price * qty

        subtotal += total

        product_data.append([
        item.product.name,
        str(qty),
        f"₹{price:.2f}",
        f"₹{total:.2f}",
    ])

    product_table = Table(
        product_data,
        colWidths=[3 * inch, 0.7 * inch, 1.2 * inch, 1.2 * inch]
    )

    product_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, -1), "CustomFont"),
    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ("ALIGN", (-1, 1), (-1, -1), "RIGHT"),
    ("GRID", (0, 0), (-1, -1), 0.8, colors.grey),
]))

    elements.append(product_table)
    elements.append(Spacer(1, 20))

# ================= TOTAL =================

    delivery_charge = Decimal("0.00") if subtotal >= 999 else Decimal("50.00")
    grand_total = subtotal + delivery_charge

    charges_data = [
    ["Description", "Amount"],
    ["Subtotal", f"₹{subtotal:.2f}"],
    ["Delivery Charge", f"₹{delivery_charge:.2f}"],
    ["Grand Total", f"₹{grand_total:.2f}"],
    ]

    charges_table = Table(
    charges_data,
    colWidths=[3 * inch, 1.5 * inch]
    )

    charges_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, -1), "CustomFont"),
    ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ("GRID", (0, 0), (-1, -1), 0.8, colors.grey),
    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#dbeafe")),
    ]))

    elements.append(charges_table)
    elements.append(Spacer(1, 25))

# ================= FOOTER =================

    footer = Paragraph("""
    <b>Terms & Conditions:</b><br/>
    • Goods once sold will not be taken back.<br/>
    • Warranty as per manufacturer policy.<br/>
    • This is a computer-generated invoice.<br/>
    Thank you for shopping with Optiview!
    """, styles["Normal"])

    elements.append(footer)

# ================= BUILD PDF =================

    doc.build(elements)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice_{order.id}.pdf"'
    return response



@login_required
def return_request(request, item_id):

    item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user
    )

    # ❌ Only delivered
    if item.status != "delivered":
        return redirect("app:order_history")

    if item.return_status != "none":
        return redirect("app:order_history")

    # ✅ Get quantity
    try:
        qty = int(request.POST.get("quantity", 1))
    except:
        qty = 1

    # ❗ Validation
    if qty <= 0 or qty > item.quantity:
        return redirect("app:order_history")

    # ✅ Reduce quantity
    item.quantity -= qty

    # ✅ Mark return request
    item.return_status = "requested"

    # 💰 Refund request (NO MESSAGE)
    if item.order.payment_method.upper() == "ONLINE":
        item.refund_status = "initiated"

    # ✅ If full return → mark complete state
    if item.quantity == 0:
        item.status = "returned"   # optional (or keep delivered)

    item.save()

    return redirect("app:order_history")