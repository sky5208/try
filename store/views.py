from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse
from store.models import Category,Product,Cart,CartItem,Order,OrderItem
from store.forms import signUpForm
from django.contrib.auth.models import Group,User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,authenticate,logout
from django.core.paginator import Paginator,EmptyPage,InvalidPage
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe


# Create your views here.
def index(request,category_slug=None):
    products = None
    category_page = None
    #toys -> สินค้าหมวดหมู่ของเล่น
    if category_slug != None:
        category_page = get_object_or_404(Category,slug=category_slug)
        products = Product.objects.all().filter(category=category_page,available=True)
    else:
        products = Product.objects.all().filter(available=True)  # Access the "objects" attribute on the "Product" model
    paginator = Paginator(products,3)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1

    try:
        productperPage = paginator.page(page)
    except (EmptyPage,InvalidPage):
        productperPage = paginator.page(paginator.num_pages)
    
    return render(request, 'index.html', {'products': productperPage,'category':category_page})



def productPage(request,category_slug,product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug,slug=product_slug)
    except Exception as e:
        raise e
    return render(request,'product.html',{'product':product})

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        request.session.create()
    return cart



@login_required(login_url='signIn')
def addCart(request, product_id):
    # รหัสสินค้า 1
    # ดึงสินค้าตามรหัสสินค้า
    product = Product.objects.get(id=product_id)
    
    # สร้างตระกร้าสินค้า (using get_or_create)
    cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))

    try:
        # ซื้อรายการสินค้าซ้ำ
        cart_item = CartItem.objects.get(product=product, cart=cart)
        
        # Check if adding one more item exceeds the available stock
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            cart_item.save()
    except CartItem.DoesNotExist:
        # ซื้อครั้งแรก
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1
        )
    
    return redirect('cartdetail')



def cartdetail(request):
    total = 0
    counter = 0
    cart_items = None
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for item in cart_items:
            total += (item.product.price * item.quantity)
            counter += item.quantity
    except Cart.DoesNotExist:
        pass  # Handle the case where the cart does not exist

    stripe.api_key = settings.SECRET_KEY
    stripe_total = int(total * 100)
    description = 'Payment Online'
    data_key = settings.PUBLIC_KEY

    if request.method == 'POST':
        try:
            token = request.POST['stripeToken']
            email = request.POST['stripeEmail']
            name = request.POST['stripeBillingName']
            address = request.POST['stripeBillingAddressLine1']
            city = request.POST['stripeBillingAddressCity']
            postcode = request.POST['stripeBillingAddressZip']

            customer = stripe.Customer.create(
                email=email,
                source=token
            )
            charge = stripe.Charge.create(
                amount=stripe_total,
                currency='thb',
                description=description,
                customer=customer.id
            )

            # Save order information
            order = Order.objects.create(
                name=name,
                address=address,
                city=city,
                postcode=postcode,
                total=total,
                email=email,
                token = token
            )
            order.save()

            # Save order items
            for item in cart_items:
                order_item = OrderItem.objects.create(
                    product=item.product.name,
                    quantity=item.quantity,
                    price=item.product.price,
                    order=order
                )
                order_item.save()

                # Reduce product stock
                product = Product.objects.get(id=item.product.id)
                product.stock = int(product.stock - order_item.quantity)
                product.save()

                item.delete()

            return redirect('thankyou')

        except stripe.error.CardError as e:
            return False, e

    return render(request, 'cartdetail.html',
                  dict(cart_items=cart_items, total=total, counter=counter,
                       data_key=data_key, stripe_total=stripe_total,
                       description=description))

def removeCart(request,product_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product,id = product_id)
    cartItem =  CartItem.objects.get(product = product, cart = cart)
    cartItem.delete()
    return redirect('cartdetail')

def signupView(request):
    if request.method == 'POST':
        # บันทึกข้อมูลuser
        form = signUpForm(request.POST)
        if form.is_valid():
            form.save()
        # บันทึก group Customer
        # ดึง username มาใช้
            username = form.cleaned_data.get('username')
            # ดีงข้อมูลจากฐาาข้อมูล
            signUpUser = User.objects.get(username = username)
            # จัด group
            customer_group = Group.objects.get(name = 'Customer')
            customer_group.user_set.add(signUpUser)

    else:
        form = signUpForm()
    return render(request,"signup.html",{'form':form})

def signinView(request):
    if request.method == 'POST':
        form = AuthenticationForm(data = request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                return redirect('home')
            else:
                return redirect('signUp')
    else:
        form =AuthenticationForm()
    return render(request,'signin.html',{'form':form})

def signOutView(request):
    logout(request)
    return redirect('signIn')

def search(request):
    products = Product.objects.filter(name__contains = request.GET['title'])
    return render(request,'index.html',{'products':products})

def orderHistory(request):
    if request.user.is_authenticated:
        email = str(request.user.email)
        orders = Order.objects.filter(email=email)
    return render(request,'order.html',{'orders':orders})
 
def viewOrder(request,order_id):
    if request.user.is_authenticated:
        email = str(request.user.email)
        order = Order.objects.get(email=email,id=order_id)
        orderitem = OrderItem.objects.filter(order=order)
    return render(request,'viewOrder.html',{'order':order,'order_item':orderitem})    

def thankyou(request):
    return render(request,'thankyou.html')
