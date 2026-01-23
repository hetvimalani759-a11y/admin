from django.shortcuts import render
from adminpanel.models import Product, Lens , Order
from django.contrib.auth.decorators import login_required
#from django.contrib.auth import authenticate, login


  # import models from adminpanel

def product_list(request):
    products = Product.objects.all()  # get all products
    return render(request, 'app/product_list.html', {'products': products})

def lens_list(request):
    lenses = Lens.objects.all()  # get all lenses
    return render(request, 'app/lens_list.html', {'lenses': lenses})



def home(request):
    return render(request, 'app/index.html')

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

def shop(request):
    return render(request, 'app/shop.html', {'products': products})


def product_detail(request, id):
    product = next(p for p in products if p['id'] == id)
    return render(request, 'app/product_detail.html', {'product': product})

