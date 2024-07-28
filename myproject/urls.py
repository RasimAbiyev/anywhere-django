"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from myapp import views
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from paypal.standard.ipn import urls as paypal_urls

urlpatterns = [
    # myproject
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),

    # Payment Integration
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('paypal/', include(paypal_urls)),
    path('product/<int:id>/', views.product_detail, name='detail'),
    path('product/<int:id>/payment/', views.payment_process, name='payment_process'),
    path('product/<int:id>/detail/', views.product_detail, name='product-detail'),
    path('payment-done/', views.payment_done, name='payment_done'),
    path('payment-cancelled/', views.payment_cancelled, name='payment_cancelled'),

    # login, logout
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Async views 
    path('async-example/', views.async_example_view, name='async_example'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
