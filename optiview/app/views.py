from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from decimal import Decimal
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import razorpay
from django.conf import settings
from io import BytesIO
import os
import qrcode

from adminpanel.models import Product, Category, Notification, Order, OrderItem,DashboardImage,ProductVariant,ProductVariantImage,Color,Brand
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







def shop(request):
    categories = Category.objects.all()
    colors = Color.objects.all()
    brands = Brand.objects.all()
    
    # Hardcoded choices for Gender and Frame Type
    genders = [
        {'id': 'male', 'name': 'Male'},
        {'id': 'female', 'name': 'Female'},
        {'id': 'unisex', 'name': 'Unisex'},
    ]
    
    frame_types = [
        {'id': 'full-rim', 'name': 'Full Rim'},
        {'id': 'half-rim', 'name': 'Half Rim'},
        {'id': 'rimless', 'name': 'Rimless'},
    ]

    # Capture selected filters
    selected_category = request.GET.get('category')
    selected_colors = request.GET.getlist('color')
    selected_genders = [x.lower() for x in request.GET.getlist('gender')]
    selected_frames = [x.lower() for x in request.GET.getlist('frame_type')]
    selected_brands = request.GET.getlist('brand')
    stock_filter = request.GET.get('stock')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    wishlist_ids = []
    products = Product.objects.all()

    # Apply filters
    if selected_category:
        products = products.filter(category_id=selected_category)

    if selected_colors:
        products = products.filter(variants__color__id__in=selected_colors).distinct()
    
    if selected_genders:
        products = products.filter(gender__in=selected_genders)
    if selected_frames:
        products = products.filter(frame_type__in=selected_frames)


    if selected_brands:
        products = products.filter(brand__id__in=selected_brands)

    if stock_filter:
        products = products.filter(stock__gt=0)

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    if request.user.is_authenticated and is_customer(request.user):
        wishlist_ids = Wishlist.objects.filter(user=request.user).values_list("product_id", flat=True)

    context = {
        'categories': categories,
        'colors': colors,
        'genders': genders,
        'frame_types': frame_types,
        'brands': brands,
        'products': products,
        'selected_category': selected_category,
        'selected_colors': selected_colors,
        'selected_genders': selected_genders,
        'selected_frames': selected_frames,
        'selected_brands': selected_brands,
        'wishlist_ids': wishlist_ids,
    }

    return render(request, 'app/shop.html', context)


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    wishlist_ids = []

    if request.user.is_authenticated and is_customer(request.user):
        wishlist_ids = Wishlist.objects.filter(user=request.user).values_list("product_id", flat=True)

    return render(request, "app/product_detail.html", {
        "product": product,
        "wishlist_ids": wishlist_ids
    })


def about(request):
    return render(request, "app/about.html")


def contact(request):
    return render(request, "app/contact.html")


# ==========================
# 🔐 AUTH (Customer Panel)
# ==========================

def register_view(request):
    if request.user.is_authenticated and is_customer(request.user):
        return redirect("app:home")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Passwords do not match!")
            return redirect("app:register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("app:register")

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully! Please login.")
        return redirect("app:login")

    return render(request, "app/register.html")


def login_view(request):
    if request.user.is_authenticated and is_customer(request.user):
        return redirect("app:home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user and is_customer(user):
            # Separate session for customer panel
            auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            request.session.set_expiry(0)  # optional, expire on browser close
            request.session.save()

            response = redirect("app:home")
            response.set_cookie("customer_sessionid", request.session.session_key)
            return response

        messages.error(request, "Invalid credentials or not a customer account.")
        return redirect("app:login")

    return render(request, "app/login.html")


@login_required
@user_passes_test(is_customer, login_url="app:login")
def customer_logout(request):
    auth_logout(request)
    response = redirect("app:home")
    response.delete_cookie("customer_sessionid")
    return response


# ==========================
# 🔐 CUSTOMER ONLY
# ==========================
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
        return redirect("app:shop")

    count = Cart.objects.filter(user=request.user).count()
    return JsonResponse({"success": True, "cart_count": count})


@login_required
def cart_view(request):
    items = Cart.objects.filter(user=request.user)
    summary = _cart_summary(request.user)

    return render(request, "app/cart.html", summary)


@login_required
def cart_count(request):
    return JsonResponse({"count": Cart.objects.filter(user=request.user).count()})




def _cart_summary(user):
    items = Cart.objects.filter(user=user).select_related("product")

    original_total = Decimal("0.00")
    total = Decimal("0.00")

    for item in items:
        product = item.product
        quantity = item.quantity

        base_price = product.price
        final_price = product.get_final_price()

        original_total += base_price * quantity
        total += final_price * quantity

    discount_total = original_total - total

    delivery_charge = Decimal("0.00") if total >= 999 else Decimal("50.00")
    grand_total = total + delivery_charge

    return {
        "items": items,
        "items_count": items.count(),
        "original_total": int(original_total),
        "discount_total": int(discount_total),
        "delivery_charge": int(delivery_charge),
        "grand_total": int(grand_total),
        "total_saved": int(discount_total),
        "total": int(total),
    }


@login_required
def increase_qty(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)

    if item.quantity >= item.product.stock:
        return JsonResponse({"success": False, "message": f"Only {item.product.stock} items in stock."})

    item.quantity += 1
    item.save()
    return JsonResponse({"success": True, "quantity": item.quantity, "summary": _cart_summary(request.user)})


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


@user_passes_test(is_customer, login_url="app:login")
def wishlist_view(request):
    products = Product.objects.filter(wishlist__user=request.user)
    wishlist_ids = products.values_list("id", flat=True)
    return render(request, "app/wishlist.html", {"products": products, "wishlist_ids": wishlist_ids})


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

@login_required


def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)

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
            product = item.product
            price = product.get_final_price()
            line_total = price * item.quantity
            total_amount += line_total

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=price
            )

            # Reduce stock
            product.stock -= item.quantity
            product.save()

        order.total_amount = total_amount

        payment_method = request.POST.get("payment")

        # ✅ FIXED PAYMENT LOGIC
        if payment_method == "ONLINE":
            if request.POST.get("razorpay_payment_id"):
                order.payment_status = True   # Paid
            else:
                order.payment_status = False  # Failed
        else:
            order.payment_status = False  # COD → Not paid yet

        order.save()
        cart_items.delete()

        return redirect("app:order_success")

    # ---- GET METHOD ----
    subtotal = sum(
        item.product.get_final_price() * item.quantity
        for item in cart_items
    )

    delivery = 0 if subtotal >= 999 else 50
    total = subtotal + delivery

    saved_amount = sum(
        (item.product.price - item.product.get_final_price()) * item.quantity
        for item in cart_items
        if item.product.get_best_offer()
    )

    return render(request, "app/checkout.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "delivery": delivery,
        "total": total,
        "saved_amount": saved_amount,
    })


# ==========================
# 📦 ORDERS
# ==========================

@user_passes_test(is_customer, login_url="app:login")

# views.py


def order_history(request):
    order_status_order = ["Placed", "Shipped", "Delivered"]

    orders = Order.objects.filter(user=request.user).prefetch_related("items__product")

    orders_with_timeline = []
    for order in orders:
        # Determine current index in timeline
        current_index = order_status_order.index(order.status) if order.status in order_status_order else 0

        # Create a timeline list for template
        timeline = []
        for i, status in enumerate(order_status_order):
            timeline.append({
                "status": status,
                "active": i <= current_index
            })

        orders_with_timeline.append({
            "order": order,
            "timeline": timeline
        })

    context = {
        "orders": orders_with_timeline
    }
    return render(request, "app/order_history.html", context)





@user_passes_test(is_customer, login_url="app:login")
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all()
    return render(request, "app/order_detail.html", {"order": order, "items": items})


@user_passes_test(is_customer, login_url="app:login")
def order_success(request):
    return render(request, "app/order_success.html")


@login_required
@user_passes_test(is_customer, login_url="app:login")
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status not in ["Delivered", "Cancelled"]:
        order.status = "Cancelled"
        order.save()
    return redirect("app:order_history")

@login_required
@user_passes_test(is_customer, login_url="app:login")
def order_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.select_related("product")

    # ✅ Unicode ₹ support
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36)

    styles = getSampleStyleSheet()
    styles["Normal"].fontName = "HeiseiMin-W3"

    elements = []

    # ================= HEADER =================
    logo_path = os.path.join(settings.BASE_DIR, "static", "images", "logo.png")
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=110, height=45)
    else:
        logo = Paragraph("<b>Optiview</b>", styles["Title"])

    company_info = Paragraph("""<b>Optiview Pvt Ltd</b><br/>
        Premium Optical Store<br/>
        support@optiview.com<br/>
        +91 98765 43210
    """, styles["Normal"])

    header_table = Table([[logo, company_info]], colWidths=[2.5 * inch, 3.5 * inch])
    header_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # ================= TITLE =================
    title_style = ParagraphStyle("TitleStyle", fontName="HeiseiMin-W3", fontSize=22, alignment=1, spaceAfter=16)
    elements.append(Paragraph("INVOICE", title_style))

    # ================= CUSTOMER + META =================
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

    info_table = Table([[left, right]], colWidths=[3.5 * inch, 2.5 * inch])
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

    # ================= PRODUCTS TABLE =================
    data = [["Product", "Qty", "Price", "GST (18%)", "Total"]]

    subtotal = Decimal("0.00")
    gst_total = Decimal("0.00")
    gst_rate = Decimal("0.18")

    for item in items:
        price = Decimal(item.product.get_final_price())
        qty = Decimal(item.quantity)
        line_total = price * qty
        gst = (line_total * gst_rate).quantize(Decimal("0.01"))

        subtotal += line_total
        gst_total += gst

        data.append([
            item.product.name,
            str(qty),
            f"₹{price:.2f}",
            f"₹{gst:.2f}",
            f"₹{(line_total + gst):.2f}",
        ])

    grand_total = subtotal + gst_total

    data.append(["", "", "Subtotal", "", f"₹{subtotal:.2f}"])
    data.append(["", "", "GST (18%)", "", f"₹{gst_total:.2f}"])
    data.append(["", "", "Grand Total", "", f"₹{grand_total:.2f}"])

    table = Table(data, colWidths=[2.3 * inch, 0.6 * inch, 1 * inch, 1 * inch, 1.1 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "HeiseiMin-W3"),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.8, colors.grey),
        ("BACKGROUND", (0, -3), (-1, -1), colors.HexColor("#dbeafe")),
        ("SPAN", (0, -3), (2, -3)),
        ("SPAN", (0, -2), (2, -2)),
        ("SPAN", (0, -1), (2, -1)),
        ("ALIGN", (3, -3), (-1, -1), "RIGHT"),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 25))

    # ================= QR PAYMENT =================
    pay_url = f"https://optiview.com/pay/{order.id}"
    qr_img = qrcode.make(pay_url)
    qr_path = os.path.join(settings.MEDIA_ROOT, f"qr_{order.id}.png")
    qr_img.save(qr_path)
    qr = Image(qr_path, width=90, height=90)

    qr_text = Paragraph("<b>Scan to Pay</b><br/>UPI / NetBanking / Cards", styles["Normal"])
    qr_table = Table([[qr, qr_text]], colWidths=[1.2 * inch, 2 * inch])
    qr_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    elements.append(qr_table)
    elements.append(Spacer(1, 18))

    # ================= SIGNATURE =================
    sign_path = os.path.join(settings.BASE_DIR, "static", "images", "signature.png")
    if os.path.exists(sign_path):
        elements.append(Image(sign_path, width=120, height=45))
    elements.append(Paragraph("<b>Authorized Signature</b>", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # ================= FOOTER =================
    footer = Paragraph("""
        <b>Terms & Conditions:</b><br/>
        • Goods once sold will not be taken back.<br/>
        • Warranty as per manufacturer policy.<br/>
        • This is a computer-generated invoice and does not require signature.<br/>
        Thank you for shopping with Optiview!
    """, styles["Normal"])
    elements.append(footer)

    doc.build(elements)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice_{order.id}.pdf"'
    return response
