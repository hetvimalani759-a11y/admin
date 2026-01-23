from django.shortcuts import render
from adminpanel.models import Product, Lens , Order
from django.contrib.auth.decorators import login_required
#from django.contrib.auth import authenticate, login


<<<<<<< HEAD
  # import models from adminpanel

def product_list(request):
    products = Product.objects.all()  # get all products
    return render(request, 'app/product_list.html', {'products': products})

def lens_list(request):
    lenses = Lens.objects.all()  # get all lenses
    return render(request, 'app/lens_list.html', {'lenses': lenses})



def home(request):
    return render(request, 'app/index.html')
=======


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
        messages.success(request, "Account created! Please login.")
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
>>>>>>> dfa612ace511239616ffd3fd5abd28f70517e88d

def about(request):
    return render(request, 'app/about.html')
def contact(request):
    return render(request,'app/contact.html')
def shop(request):
    return render(request, 'app/shop.html')


products = [
    {
        'id': 1,
        'name': 'Sport Goggles',
        'price': 1499,
        'image': 'images/product1.jpg',
        'description': 'Perfect for outdoor sports and riding.',
        'category': 'Men',
        'subcategory': 'Sport'
    },
    
    {
        'id': 2,
        'name': 'Classic Goggles',
        'price': 1299,
        'image': 'images/product2.jpg',
        'description': 'Stylish classic goggles for daily use.',
        'category': 'Women',
        'subcategory': 'Classic'
    }
]
<<<<<<< HEAD

def shop(request):
    return render(request, 'app/shop.html', {'products': products})


def product_detail(request, id):
    product = next(p for p in products if p['id'] == id)
    return render(request, 'app/product_detail.html', {'product': product})

=======
>>>>>>> dfa612ace511239616ffd3fd5abd28f70517e88d
