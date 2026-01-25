from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from adminpanel.models import Product, Lens, Order


# -------------------- AUTH --------------------

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register')

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')

    return render(request, "app/register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password!")
            return redirect('login')

    return render(request, "app/login.html")


def logout_view(request):
    user = request.user
    logout(request)
    user.is_active = False
    user.save()
    return redirect("home")



# -------------------- HOME --------------------

def home(request):
    return render(request, "app/index.html")


# -------------------- PRODUCT & LENS --------------------

def product_list(request):
    products = Product.objects.all()
    return render(request, 'app/product_list.html', {'products': products})


def lens_list(request):
    lenses = Lens.objects.all()
    return render(request, 'app/lens_list.html', {'lenses': lenses})


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'app/product_detail.html', {'product': product})


def shop(request):
    products = Product.objects.all()
    return render(request, 'app/shop.html', {'products': products})


# -------------------- STATIC PAGES --------------------

def about(request):
    return render(request, 'app/about.html')


def contact(request):
    return render(request, 'app/contact.html')
from .models import Notification

def notifications(request):
    data = Notification.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "app/notifications.html", {"notifications": data})
def mark_read(request, id):
    Notification.objects.filter(id=id, user=request.user).update(is_read=True)
    return redirect("notifications")
