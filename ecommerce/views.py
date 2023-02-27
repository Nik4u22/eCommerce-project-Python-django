from django.shortcuts import render
from .models import *
from math import ceil
# Create your views here.

def user_home(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
        
    params = {'allProds': allProds}
    
    return render(request, 'authentication/home.html', params)

def get_product(request , slug):
    print("slug=", slug)
    try:
        product = Product.objects.get(slug =slug)
        
    except Exception as e:
        print(e)
    
    return render(request, 'ecommerce/product.html', context = {'product' : product})
