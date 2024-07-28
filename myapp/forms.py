from django import forms
from .models import User, Product, Advertisement, Comment, Complaint
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

# Custom User
class UserProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['profile_picture', 'username', 'email', 'first_name', 'last_name', 'bio', 'birth_date']

# Search Bar
class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)

# Advertisement status (Approved, Rejected, Processing)
class AdvertisementStatusForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['status']

# Commenting logic + Complaint
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['reason', 'details']

# register
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')

# Create Product
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'image']