from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Product, Advertisement, Comment, Complaint


# Custom User
admin.site.register(User, UserAdmin)

# Advertisement status (Approved, Rejected, Processing)
@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'status')
    list_filter = ('status',)
    search_fields = ('title', 'description')

# Commenting logic, Complaint
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1

class ComplaintInline(admin.TabularInline):
    model = Complaint
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'total_comments', 'total_complaints', 'price', 'views')
    list_filter = ('name', 'price')
    search_fields = ('name', 'description')
    inlines = [CommentInline, ComplaintInline]
    ordering = ('-price',)

    def total_comments(self, obj):
        return obj.comments.count()
    total_comments.short_description = 'Total Comments'

    def total_complaints(self, obj):
        return obj.complaints.count()
    total_complaints.short_description = 'Total Complaints'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'content', 'created_at')
    list_filter = ('created_at', 'product')
    search_fields = ('content',)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'reason', 'created_at')
    list_filter = ('created_at', 'product')
    search_fields = ('reason',)