import os
import json
import uuid
import asyncio
import smtplib
import requests
from io import BytesIO
from django.urls import reverse
from .tasks import process_data
from django.conf import settings
from rest_framework import viewsets
from django.contrib import messages
from reportlab.pdfgen import canvas
from email.mime.text import MIMEText
from celery.result import AsyncResult
from django.contrib.auth import login
from .serializers import ItemSerializer
from .serializers import PromotionSerializer
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from myapp.credentials import TELEGRAM_API_URL, URL
from paypal.standard.forms import PayPalPaymentsForm
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .utils import add_watermark, crop_image, create_thumbnail
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from .models import Item, Promotion, Product, Advertisement, Comment, Complaint, Cart, CartItem
from .forms import UserProfileForm, ProductForm, SearchForm, AdvertisementStatusForm, CommentForm, ComplaintForm, CustomUserCreationForm


# Home page
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

@login_required
def index(request):
    return render(request, 'home.html')

# Rest API
class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

# AJAX
class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer

def promotions_view(request):
    return render(request, 'index.html')

# Payment Integration
def payment_process(request, id):
    product = get_object_or_404(Product, id=id)
    cart = Cart.objects.get(user=request.user)
    
    total_price = sum(item.product.price * item.quantity for item in cart.items.all())
    
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": str(total_price),
        "item_name": "Cart items",
        "invoice": str(cart.id),
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return_url": request.build_absolute_uri(reverse('payment_done')),
        "cancel_return": request.build_absolute_uri(reverse('payment_cancelled')),
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    
    return render(request, 'payment/process.html', {'cart': cart, 'form': form, 'total_price': total_price})
def payment_done(request):
    return render(request, 'payment/done.html')

def payment_cancelled(request):
    return render(request, 'payment/cancelled.html')

# Session
def set_session(request):
    request.session['username'] = 'john_doe'
    return HttpResponse('Session data set successfully.')

def get_session(request):
    username = request.session.get('username', 'Guest')
    return HttpResponse(f'Username from session: {username}')

# Likes, dislikes, favorite, views count
def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

# @login_required
def update_product_views(id):
    product = Product.objects.get(id=id)
    # print(f"Initial views count: {product.views}")
    product.views = (product.views or 0) + 1
    product.save()
    product = Product.objects.get(id=id)
    # print(f"Final views count: {product.views}")
update_product_views(1)

@login_required
def like_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.like.add(request.user)
    return redirect(reverse('detail', kwargs={'id': product.id}))

@login_required
def dislike_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.like.remove(request.user)
    return redirect(reverse('detail', kwargs={'id': product.id}))

@login_required
def favorite_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.user in product.favorite.all():
        product.favorite.remove(request.user)
    else:
        product.favorite.add(request.user)
    return redirect(reverse('user_favorites'))

@login_required
def remove_favorite_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.user in product.favorite.all():
        product.favorite.remove(request.user)
    return redirect(reverse('detail', kwargs={'id': id}))

@login_required
def user_favorites(request):
    user_favorites = Product.objects.filter(favorite=request.user)
    return render(request, 'user_favorite.html', {'user_favorites': user_favorites})

# Celery, Redis
def trigger_task(request):
    process_data.delay('sample data')
    return HttpResponse("Task triggered!")

# Custom User
@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'profile_edit.html', {'form': form})

# Async views 
async def async_example_view(request):
    await asyncio.sleep(1)
    return JsonResponse({'message': 'Async operation complete'})

# Automated Bot
def setwebhook(request):
  response = requests.post(TELEGRAM_API_URL+ "setWebhook?url=" + URL).json()
  return HttpResponse(f"{response}")

@csrf_exempt
def telegram_bot(request):
  if request.method == 'POST':
    update = json.loads(request.body.decode('utf-8'))
    chat_id = update['message']['chat']['id']
    text = update['message']['text']
    send_message("sendMessage", {
      'chat_id': chat_id,
      'text': f'your message {text}'
    })
  return HttpResponse('ok')

def send_message(method, data):
  return requests.post(TELEGRAM_API_URL + method, data)

# Send Mail (Dynamic mails, attached images, invoice.pdf)
def send_notification_view(request):
    if request.method == "POST":
        data = request.POST
        to_email = data.get("to_email")
        title = data.get("title")
        message = data.get("message")
        pdf_buffer = BytesIO()
        p = canvas.Canvas(pdf_buffer)
        p.drawString(100, 750, "Invoice")
        p.drawString(100, 730, f"Title: {title}")
        p.drawString(100, 710, f"Message: {message}")
        p.showPage()
        p.save()
        pdf_buffer.seek(0)
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = to_email
        msg['Subject'] = title
        msg.attach(MIMEText(message, 'plain'))
        pdf_attachment = MIMEApplication(pdf_buffer.read(), _subtype='pdf')
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename='invoice.pdf')
        msg.attach(pdf_attachment)
        image_path = os.path.join(settings.BASE_DIR, 'myapp/static/images/sample.png')
        if os.path.exists(image_path):
            with open(image_path, 'rb') as image_file:
                image_attachment = MIMEApplication(image_file.read(), _subtype='png')
                image_attachment.add_header('Content-Disposition', 'attachment', filename='sample.png')
                msg.attach(image_attachment)
        else:
            return HttpResponse("Image file not found.")
        try:
            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.set_debuglevel(1)  # Enable debug output
                server.starttls()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.send_message(msg)
            return HttpResponse("Email sent successfully!")
        except Exception as e:
            return HttpResponse(f"Failed to send email: {e}")
    return render(request, 'form.html')

# Working with image. (Watermark, Crop, Thumbnail)
def process_image(request):
    if request.method == 'POST':
        image_file = request.FILES.get('image')
        watermark_file = request.FILES.get('watermark')
        crop_box_str = request.POST.get('crop_box', '0,0,100,100')
        thumbnail_size_str = request.POST.get('thumbnail_size', '200,200')
        if not image_file or not watermark_file:
            return HttpResponse('Both image and watermark are required.', status=400)
        crop_box = tuple(map(int, crop_box_str.split(',')))
        thumbnail_size = tuple(map(int, thumbnail_size_str.split(',')))
        image_path = os.path.join('media/images', image_file.name)
        watermark_path = os.path.join('media/watermarks', watermark_file.name)
        with open(image_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        with open(watermark_path, 'wb+') as destination:
            for chunk in watermark_file.chunks():
                destination.write(chunk)
        watermarked_image_path = os.path.join('media/images', 'watermarked_image.jpg')
        cropped_image_path = os.path.join('media/images', 'cropped_image.jpg')
        thumbnail_image_path = os.path.join('media/images', 'thumbnail.jpg')
        add_watermark(image_path, watermark_path, watermarked_image_path)
        crop_image(image_path, crop_box, cropped_image_path)
        create_thumbnail(image_path, thumbnail_size, thumbnail_image_path)
        return HttpResponse('Image processed successfully!')
    return render(request, 'image_app/upload_image.html')

# Search Bar
def search(request):
    form = SearchForm(request.GET or None)
    results = []
    if form.is_valid():
        query = form.cleaned_data['query']
        results = Product.objects.filter(name__icontains=query)
    return render(request, 'search_results.html', {
        'form': form,
        'results': results
    })

# Advertisement status (Approved, Rejected, Processing) 
def advertisement_list(request):
    advertisements = Advertisement.objects.all()
    return render(request, 'advertisement_list.html', {'advertisements': advertisements})

def update_advertisement_status(request, ad_id):
    advertisement = get_object_or_404(Advertisement, id=ad_id)
    if request.method == 'POST':
        form = AdvertisementStatusForm(request.POST, instance=advertisement)
        if form.is_valid():
            form.save()
            return redirect('advertisement_list')
    else:
        form = AdvertisementStatusForm(instance=advertisement)
    return render(request, 'update_advertisement_status.html', {
        'form': form,
        'advertisement': advertisement
    })

# Messenger. Sockets. Chat logic.
def chatPage(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login-user")
    context = {}
    return render(request, "myapp/chatPage.html", context)

# Commenting logic + Complaint
@login_required
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    comments = product.comments.all()
    comment_form = CommentForm()
    complaint_form = ComplaintForm()
    if request.method == 'POST':
        if 'submit_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.product = product
                comment.user = request.user
                comment.save()
                return redirect('product_detail', id=id)
        elif 'submit_complaint' in request.POST:
            complaint_form = ComplaintForm(request.POST)
            if complaint_form.is_valid():
                complaint = complaint_form.save(commit=False)
                complaint.product = product
                complaint.user = request.user
                complaint.save()
                return redirect('product_detail', id=id)
    return render(request, 'product.html', {
        'product': product,
        'comments': comments,
        'comment_form': comment_form,
        'complaint_form': complaint_form,
    })
@login_required
def delete_comment(request, id):
    comment = get_object_or_404(Comment, id=id)
    if comment.user == request.user or request.user.is_superuser:
        comment.delete()
        return redirect('product_detail', id=comment.product.id)
    return HttpResponseForbidden("You are not allowed to delete this comment.")

@login_required
def delete_complaint(request, id):
    complaint = get_object_or_404(Complaint, id=id)
    if complaint.user == request.user or request.user.is_superuser:
        complaint.delete()
        return redirect('product_detail', id=complaint.product.id)
    return HttpResponseForbidden("You are not allowed to delete this complaint.")

# register
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Create Product
@login_required
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductForm()
    return render(request, 'create_product.html', {'form': form})

# Add to Cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item = CartItem.objects.filter(cart=cart, product=product).first()
    if cart_item:
        return redirect('view_cart')
    else:
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        return redirect('view_cart')

@login_required
def increment_quantity(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = CartItem.objects.filter(cart=cart, product=product).first()
    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')

@login_required
def decrement_quantity(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = CartItem.objects.filter(cart=cart, product=product).first()
    if cart_item and cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    elif cart_item:
        cart_item.delete()
    return redirect('view_cart')

@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = CartItem.objects.filter(cart=cart, product=product).first()
    if cart_item:
        cart_item.delete()
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/view_cart.html', {'cart': cart})