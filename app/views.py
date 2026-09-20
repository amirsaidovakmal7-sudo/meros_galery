from django.shortcuts import render, redirect
from .models import *






# Порядок категорий магазина на сайте (как в структуре главной: main2–main3).
# Категории, которых нет в списке, идут в конце в порядке из админки.
SHOP_CATEGORY_ORDER = ['retail', 'vintage', 'art', 'secondhand']


def ordered_categories():
    def sort_key(category):
        key = category.category_name.replace(' ', '').lower()
        position = SHOP_CATEGORY_ORDER.index(key) if key in SHOP_CATEGORY_ORDER else len(SHOP_CATEGORY_ORDER)
        return (position, category.my_order)
    return sorted(ProductCategory.objects.all(), key=sort_key)


def home_page(request):
    news = News.objects.all()
    product_categories = ordered_categories()
    products = Products.objects.all()
    events = Events.objects.all()
    masterclasses = Masterclasses.objects.all()
    feedbacks = Feedbacks.objects.all()
    context = {'news': news, 'categories': product_categories, 'products': products, 'events': events, 'masterclasses': masterclasses, 'feedbacks': feedbacks}
    return render(request, 'home.html', context)


def about_page(request):
    workers = Workers.objects.all()
    context = {'workers': workers}
    return render(request, 'about.html', context)



def events_page(request):
    events = Events.objects.all()
    masterclasses = Masterclasses.objects.all()
    context = {'events': events, 'masterclasses': masterclasses}
    return render(request, 'events.html', context)

def shop_page(request):
    products = Products.objects.all()
    product_categories = ordered_categories()
    context = {'products': products, 'product_categories': product_categories}
    return render(request, 'shop.html', context)





def news(request):
    news = News.objects.all()
    context = {'news': news}
    return render(request, 'news.html', context)


def exact_new(request, pk):
    new = News.objects.get(id=pk)
    context = {'new': new}
    return render(request, 'new.html', context)


def product_page(request, pk):
    product = Products.objects.get(id=pk)
    context = {'product': product}
    return render(request, 'product.html', context)



def event_page(request, pk):
    event = Events.objects.get(id=pk)
    context = {'event': event}
    return render(request, 'event.html', context)


def masterclass_page(request, pk):
    masterclass = Masterclasses.objects.get(id=pk)
    context = {'masterclass': masterclass}
    return render(request, 'masterclass.html', context)



def category_product(request, pk):
    category = ProductCategory.objects.get(id=pk)
    products = Products.objects.filter(product_category=category)
    context = {'products': products, 'category': category}
    if category.category_name == 'Art':
        return render(request, 'category_art.html', context)
    return render(request, 'category.html', context)




def get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def add_to_cart_product(request, pk):
    if request.method == 'POST':
        session_key = get_session_key(request)
        user_count = int(request.POST.get('user_count'))
        user_product = Products.objects.get(id=pk)
        user_cart_product = Cart.objects.filter(session_key=session_key, user_product=user_product).first()
        if user_cart_product:
            final_product = user_cart_product.user_amount + user_count
            user_cart_product.user_amount = final_product
            user_cart_product.save()
            return redirect(f'/shop/product/{pk}')
        else:
            if 1 <= user_count <= user_product.allowed_amount:
                Cart.objects.create(session_key=session_key, user_product=user_product, user_amount=user_count).save()
                return redirect(f'/shop/product/{pk}')
            return redirect(f'/shop/product/{pk}')
    return False

def add_to_cart_event(request, pk):
    if request.method == 'POST':
        session_key = get_session_key(request)
        user_count = int(request.POST.get('user_count'))
        user_event = Events.objects.get(id=pk)
        user_cart_event = Cart.objects.filter(session_key=session_key, user_event=user_event).first()
        if user_cart_event:
            final_product = user_cart_event.user_amount + user_count
            user_cart_event.user_amount = final_product
            user_cart_event.save()
            return redirect(f'/events/{pk}')
        else:
            if 1 <= user_count <= user_event.allowed_amount:
                Cart.objects.create(session_key=session_key, user_event=user_event, user_amount=user_count).save()
                return redirect(f'/events/{pk}')
            return redirect(f'/events/{pk}')
    return False

def add_to_cart_masterclass(request, pk):
    if request.method == 'POST':
        session_key = get_session_key(request)
        user_count = int(request.POST.get('user_count'))
        user_masterclass = Masterclasses.objects.get(id=pk)
        user_cart_masterclass = Cart.objects.filter(session_key=session_key, user_masterclass=user_masterclass).first()
        if user_cart_masterclass:
            final_amount = user_cart_masterclass.user_amount + user_count
            user_cart_masterclass.user_amount = final_amount
            user_cart_masterclass.save()
            return redirect(f'/events/masterclass/{pk}')
        else:
            if 1 <= user_count <= user_masterclass.allowed_amount:
                Cart.objects.create(session_key=session_key, user_masterclass=user_masterclass, user_amount=user_count).save()
                return redirect(f'/events/masterclass/{pk}')
            return redirect(f'/events/masterclass/{pk}')
    return False



def remove_from_cart_product(request, pk):
    session_key = get_session_key(request)
    product = Products.objects.get(id=pk)
    Cart.objects.filter(session_key=session_key, user_product=product).delete()
    return redirect('/cart')


def remove_from_cart_event(request, pk):
    session_key = get_session_key(request)
    event = Events.objects.get(id=pk)
    Cart.objects.filter(session_key=session_key, user_event=event).delete()
    return redirect('/cart')

def remove_from_cart_masterclass(request, pk):
    session_key = get_session_key(request)
    masterclass = Masterclasses.objects.get(id=pk)
    Cart.objects.filter(session_key=session_key, user_masterclass=masterclass).delete()
    return redirect('/cart')

def cart_page(request):
    session_key = get_session_key(request)
    cart = Cart.objects.filter(session_key=session_key)
    context = {'cart': cart}
    return render(request, 'cart.html', context)
