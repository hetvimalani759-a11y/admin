from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from adminpanel.models import Product, Lens




def shop(request):
    return render(request, 'app/shop.html', {'products': products})


def product_detail(request, id):
    product = next(p for p in products if p['id'] == id)
    return render(request, 'app/product_detail.html', {'product': product})
# -------------------- AUTH --------------------

# REGISTER
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        # EMPTY FIELD CHECK
        if not username or not password or not password2:
            messages.error(request, "All fields are required!")
            return redirect('register')

        # PASSWORD MATCH
        if password != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        # PASSWORD LENGTH
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long!")
            return redirect('register')

        # USERNAME EXISTS
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register')

        # CREATE USER
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')

    return render(request, "app/register.html")


# -------------------- HOME --------------------

def home(request):
    return render(request, "app/index.html")
# LOGIN
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


# LOGOUT → HOME
def logout_view(request):
    logout(request)
    return redirect('home')

# -------------------- PRODUCT VIEWS --------------------

def product_list(request):
    products = Product.objects.all()
    return render(request, 'app/product_list.html', {'products': products})


def lens_list(request):
    lenses = Lens.objects.all()
    return render(request, 'app/lens_list.html', {'lenses': lenses})


# -------------------- STATIC PAGES --------------------

def about(request):
    return render(request, 'app/about.html')


def contact(request):
    return render(request, 'app/contact.html')


# -------------------- SHOP DEMO DATA --------------------

products = [
    {
        'id': 1,
        'name': 'Sport Goggles',
        'price': 1499,
        'image': 'app/images/product1.jpg',
        'description': 'Perfect for outdoor sports and riding.',
        'category': 'Men',
        'subcategory': 'Sport'
    },
    
    {
        'id': 2,
        'name': 'Classic Goggles',
        'price': 1299,
        'image': 'app/images/product2.jpg',
        'description': 'Stylish classic goggles for daily use.',
        'category': 'Women',
        'subcategory': 'Classic'
    }
]