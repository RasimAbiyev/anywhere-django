from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth.views import LoginView, LogoutView

from .views import (
    ItemViewSet, PromotionViewSet, promotions_view, index, payment_done, 
    payment_cancelled, set_session, get_session, product_list, product_detail, 
    like_product, dislike_product, favorite_product, remove_favorite_product, 
    user_favorites, profile_view, edit_profile_view, telegram_bot, setwebhook, 
    send_notification_view, process_image, search, advertisement_list, login_view,
    update_advertisement_status, chatPage, delete_comment, delete_complaint, register,
    create_product, add_to_cart, view_cart, remove_from_cart, increment_quantity, decrement_quantity
)

# Rest API
router = DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'promotions', PromotionViewSet)

urlpatterns = [
    # Rest API
    path('api/', include(router.urls)),
    
    # AJAX
    path('index/', promotions_view, name='promotions'),
    
    # Home page
    path('', index, name='home'),
    
    # Payment Integration
    path('payment/done/', payment_done, name='payment_done'),
    path('payment/cancelled/', payment_cancelled, name='payment_cancelled'),
    
    # Session
    path('set-session/', set_session, name='set_session'),
    path('get-session/', get_session, name='get_session'),
    
    # Likes, dislikes, favorite, views count
    path('products/', product_list, name='product_list'),
    path('products/<int:id>/', product_detail, name='detail'),
    path('products/<int:id>/like/', like_product, name='like'),
    path('products/<int:id>/dislike/', dislike_product, name='dislike'),
    path('products/<int:id>/favorite/', favorite_product, name='favorite'),
    path('products/<int:id>/remove_favorite/', remove_favorite_product, name='remove_favorite'),
    path('user/favorites/', user_favorites, name='user_favorites'),
    
    # Custom User
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', edit_profile_view, name='edit_profile'),
    
    # Automated Bot
    path('getpost/', telegram_bot, name='telegram_bot'),
    path('setwebhook/', setwebhook, name='setwebhook'),
    
    # Send Mail (Dynamic mails, attached images, invoice.pdf)
    path('send-mail-test/', send_notification_view),
    
    # Working with image. (Watermark, Crop, Thumbnail)
    path('process/', process_image, name='process_image'),
    
    # Search Bar
    path('search/', search, name='search'),
    
    # Advertisement status (Approved, Rejected, Processing)
    path('advertisements/', advertisement_list, name='advertisement_list'),
    path('advertisement/<int:ad_id>/update-status/', update_advertisement_status, name='update_advertisement_status'),
    
    # Messenger. Sockets. Chat logic.
    path('chat/', chatPage, name='chat-page'),
    
    # Authentication
    path('login/', LoginView.as_view(template_name="myapp/LoginPage.html"), name='login-user'),
    path('logout/', LogoutView.as_view(), name='logout-user'),
    path('login/', login_view, name='login-user'),
    
    # Commenting logic + Complaint
    path('product/<int:id>/', product_detail, name='product_detail'),
    path('comment/delete/<int:id>/', delete_comment, name='delete_comment'),
    path('complaint/delete/<int:id>/', delete_complaint, name='delete_complaint'),

    # register
    path('register/', register, name='register'),

    # Create Product
    path('create-product/', create_product, name='create_product'),

    # Add to Cart
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/increment/<int:product_id>/', increment_quantity, name='increment_quantity'),
    path('cart/decrement/<int:product_id>/', decrement_quantity, name='decrement_quantity'),
]