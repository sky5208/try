from django.contrib import admin
from django.urls import path,include
from store import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path("admin/", admin.site.urls),
    path('',views.index,name='home'),
    path('category/<slug:category_slug>',views.index, name='product_by_category'),
    path('product/<slug:category_slug>/<slug:product_slug>', views.productPage, name='productDetails'),
    path('cart/add/<int:product_id>',views.addCart,name='addCart'),
    path('cartdetail/',views.cartdetail,name="cartdetail"),
    path('cart/remove/<int:product_id>',views.removeCart,name="removeCart"),
    path('account/create',views.signupView,name="signUp"),
    path('account/login',views.signinView,name="signIn"),
    path('account/logout',views.signOutView,name="signOut"),
    path('search/',views.search,name="search"),

]
# product/fashion/
# product/toys/lego
if settings.DEBUG :
    # /media/product
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
    # /static/
    urlpatterns+=static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    # /static/media/iphone.jpg