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
User = get_user_model()
from .models import (
    Product, Category, SubCategory, Offer,
    Order, OrderItem, Lens, Notification,
    CompanyInfo, DeliveryPerson,DashboardImage,ProductVariant,
    ProductVariantImage,
)

LOW_STOCK_THRESHOLD = 50


# =====================================================
# 🔐 AUTH
# =====================================================

def admin_login(request):
    if request.user.is_authenticated and is_admin(request.user):
        return redirect("adminpanel:dashboard")
    request.session.flush()

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


@login_required(login_url="adminpanel:login")
@login_required
def admin_logout(request):
    request.session.flush()
    logout(request)
    return redirect("adminpanel:login")

def add_dashboard_image(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        image = request.FILES.get('image')

        if image:  # Make sure an image is uploaded
            DashboardImage.objects.create(
                title=title,
                description=description,
                image=image
            )
            return redirect('adminpanel:dashboard')  # Go back to dashboard after adding

    return render(request, 'admin/add_dashboard_image.html')
# =====================================================
# 📊 DASHBOARD
# =====================================================

@user_passes_test(is_admin, login_url="adminpanel:login")


  # adjust as needed

def dashboard(request):
    # ---------- TOTAL COUNTS ----------
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_lenses = Lens.objects.count()
    total_users = User.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum("total_amount"))["total"] or 0

    # ---------- LATEST PRODUCT ----------
    latest_products = Product.objects.order_by("-created_at")[:1]

    # ---------- COMPANY INFO ----------
    company = CompanyInfo.objects.first()

    # ---------- NOTIFICATIONS ----------
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    notification_count = notifications.count()

    # ---------- LOW STOCK PRODUCTS ----------
    # Precompute purchased and sold quantities
    products = Product.objects.annotate(
        purchased=Sum('purchases__quantity'),
        sold=Sum('orderitem__quantity')
    )
    
    low_stock_products = [
        p for p in products 
        if (p.purchased or 0) - (p.sold or 0) <= LOW_STOCK_THRESHOLD
    ]
    low_stock_count = len(low_stock_products)

    # ---------- ORDER STATUS PIE ----------
    order_qs = Order.objects.values("status").annotate(count=Count("id"))
    order_labels = [o["status"].title() for o in order_qs]
    order_values = [o["count"] for o in order_qs]

    # ---------- WEEKLY REVENUE LINE ----------
    today = now().date()
    start_week = today - timedelta(days=today.weekday())

    revenue_qs = (
        Order.objects
        .filter(created_at__date__gte=start_week)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Sum("total_amount"))
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


# ===== Add Brand =====
def add_brand_page(request):
    brands = Brand.objects.all()
    
    if request.method == "POST":
        name = request.POST.get("name").strip()  # remove leading/trailing spaces
        if name:
            brand, created = Brand.objects.get_or_create(name=name)
            if created:
                messages.success(request, f"Brand '{name}' added successfully!")
            else:
                messages.warning(request, f"Brand '{name}' already exists.")
            return redirect('adminpanel:add_brand_page')
    
    return render(request, "admin/add_brand.html", {"brands": brands})

# ===== Add Color =====
def add_color_page(request):
    colors = Color.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        code = request.POST.get("code")  # optional hex code
        if name:
            Color.objects.create(name=name, code=code)
            return redirect('adminpanel:add_color_page')
    return render(request, "admin/add_color.html", {"colors": colors})

# =====================================================
# 🔔 NOTIFICATIONS
# =====================================================

@user_passes_test(is_admin, login_url="adminpanel:login")
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-id")
    return render(request, "admin/notifications.html", {"notifications": notifications})


@user_passes_test(is_admin, login_url="adminpanel:login")
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"status": "ok"})


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
        SubCategory.objects.create(
            category_id=request.POST.get("category"),
            name=request.POST.get("name")
        )
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
        if name and category_id:
            subcategory.name = name
            subcategory.category_id = category_id
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

@user_passes_test(is_admin, login_url="adminpanel:login")


def add_product(request):
    categories = Category.objects.all()
    brands = Brand.objects.all()
    colors = Color.objects.all()

    if request.method == "POST":
        # 1️⃣ Create Product without stock (we'll calculate total later)
        product = Product.objects.create(
            name=request.POST.get("name"),
            brand_id=request.POST.get("brand"),
            price=request.POST.get("price"),
            category_id=request.POST.get("category"),
            subcategory_id=request.POST.get("subcategory"),
            description=request.POST.get("description"),
            gender=request.POST.get("gender"),
            frame_type=request.POST.get("frame_type"),
            stock=0  # temporary, will update after summing variants
        )

        # 2️⃣ Parse variants from POST
        import re
        variant_data = {}
        for key, value in request.POST.items():
            m = re.match(r"variants\[(\d+)\]\[(\w+)\]", key)
            if m:
                index, field = m.groups()
                if index not in variant_data:
                    variant_data[index] = {}
                variant_data[index][field] = value

        total_stock = 0
        for index, variant in variant_data.items():
            color_id = variant.get("color")
            stock = int(variant.get("stock", 0))
            total_stock += stock

            # 3️⃣ Create variant
            variant_obj = ProductVariant.objects.create(
                product=product,
                color_id=color_id,
                stock=stock,
            )

            # 4️⃣ Attach images
            images = request.FILES.getlist(f"variants[{index}][images][]")
            for img in images:
                ProductVariantImage.objects.create(
                    variant=variant_obj,
                    image=img
                )

        # 5️⃣ Update total stock
        product.stock = total_stock
        product.save()

        # 6️⃣ Send notifications to all non-staff users
        for user in User.objects.filter(is_staff=False):
            Notification.objects.create(user=user, message=f"New product '{product.name}' added!")

        messages.success(request, "Product added successfully!")
        return redirect("adminpanel:product_list")

    context = {
        "categories": categories,
        "brands": brands,
        "colors": colors,
    }
    return render(request, "admin/add_product.html", context)


@user_passes_test(is_admin, login_url="adminpanel:login")
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from django.contrib.auth.decorators import user_passes_test
# from .models import Product, ProductVariant, ProductVariantImage, Category, SubCategory, Color, Brand, User, Notification

@user_passes_test(lambda u: u.is_staff, login_url="adminpanel:login")
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    subcategories = SubCategory.objects.filter(category=product.category)
    brands = Brand.objects.all()
    colors = Color.objects.all()

    if request.method == "POST":
        # --- Update main product fields ---
        product.name = request.POST.get("name")
        product.brand_id = request.POST.get("brand")
        product.category_id = request.POST.get("category")
        product.subcategory_id = request.POST.get("subcategory")
        product.price = request.POST.get("price")
        product.description = request.POST.get("description")
        product.gender = request.POST.get("gender")
        product.frame_type = request.POST.get("frame_type")

        if request.FILES.get("image"):
            product.image = request.FILES.get("image")

        product.save()

        # --- Handle variants ---
        # Delete old variants
        product.variants.all().delete()

        import re
        variant_data = {}
        for key, value in request.POST.items():
            m = re.match(r"variants\[(\d+)\]\[(\w+)\]", key)
            if m:
                idx, field = m.groups()
                if idx not in variant_data:
                    variant_data[idx] = {}
                variant_data[idx][field] = value

        total_stock = 0
        for idx, data in variant_data.items():
            color_id = data.get("color")
            stock = int(data.get("stock", 0))
            total_stock += stock

            if color_id and stock:
                variant = ProductVariant.objects.create(
                    product=product,
                    color_id=color_id,
                    stock=stock
                )

                # Handle variant images
                images = request.FILES.getlist(f"variants[{idx}][images][]")
                for img in images:
                    ProductVariantImage.objects.create(
                        variant=variant,
                        image=img
                    )

        # Update total stock
        product.stock = total_stock
        product.save()

        messages.success(request, "Product updated successfully!")
        return redirect("adminpanel:product_list")

    return render(request, "admin/edit_product.html", {
        "product": product,
        "categories": categories,
        "subcategories": subcategories,
        "brands": brands,
        "colors": colors
    })


@user_passes_test(is_admin, login_url="adminpanel:login")
def delete_product(request, id):
    Product.objects.filter(id=id).delete()
    messages.error(request, "Product deleted")
    return redirect("adminpanel:product_list")


# =====================================================
# 📦 ORDERS
# =====================================================

@user_passes_test(is_admin, login_url="adminpanel:login")
def order_list(request):
    orders = Order.objects.all().order_by("-created_at")
    orderitems = OrderItem.objects.select_related("order", "product")
    return render(request, "admin/order_list.html", {
        "orders": orders,
        "orderitems": orderitems
    })


@user_passes_test(is_admin, login_url="adminpanel:login")
def update_order_status(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get("status")
        if new_status:
            order.status = new_status
            order.save()
    return redirect("adminpanel:order_list")


# =====================================================
# 📦 LENS
# =====================================================

@user_passes_test(is_admin, login_url="adminpanel:login")
def lens_list(request):
    lenses = Lens.objects.all()
    return render(request, "admin/lens_list.html", {"lenses": lenses})


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


# adjust as needed

def low_stock_products(request):
    products = Product.objects.annotate(
        purchased=Sum('purchases__quantity'),
        sold=Sum('orderitem__quantity')
    )
    
    low_stock_products = []
    for p in products:
        stock = (p.purchased or 0) - (p.sold or 0)
        if stock <= LOW_STOCK_THRESHOLD:
            p.stock = stock  # attach stock attribute to product
            low_stock_products.append(p)

    # prepare chart data
    labels = [p.name for p in low_stock_products]
    data = [p.stock for p in low_stock_products]

    return render(request, "admin/low_stock_products.html", {
        "low_stock_products": low_stock_products,
        "labels": labels,
        "data": data,
        "low_stock_threshold": LOW_STOCK_THRESHOLD
    })


# =====================================================
# 💰 REVENUE
# =====================================================

@user_passes_test(is_admin, login_url="adminpanel:login")
def revenue_dashboard(request):
    monthly_revenue = (
        Order.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('total_amount'))
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

        Offer.objects.create(
            name=name,
            discount_type=discount_type,
            discount_value=discount_value,
            product_id=product_id or None,
            category_id=category_id or None,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active,
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
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("adminpanel:delivery_person_add")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.is_staff = True  # delivery role
        user.save()

        DeliveryPerson.objects.create(user=user, phone=phone)

        messages.success(request, "Delivery person added successfully.")
        return redirect("adminpanel:delivery_person_list")

    return render(request, "delivery/add_delivery_person.html")


# =====================================================
# 🚚 ASSIGN ORDERS
# =====================================================

@user_passes_test(is_admin, login_url="adminpanel:login")
def assign_order(request):
    orders = Order.objects.filter(status='Pending')
    delivery_persons = DeliveryPerson.objects.all()

    if request.method == "POST":
        order_id = request.POST.get("order")
        dp_id = request.POST.get("delivery_person")

        order = get_object_or_404(Order, id=order_id)
        dp = get_object_or_404(DeliveryPerson, id=dp_id)

        order.assigned_to = dp
        order.status = 'Assigned'
        order.save()

        return redirect('adminpanel:assign_order')

    return render(request, 'admin/assign_order.html', {
        'orders': orders,
        'delivery_persons': delivery_persons
    })
