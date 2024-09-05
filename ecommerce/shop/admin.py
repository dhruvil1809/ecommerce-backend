from django.contrib import admin
from .models import Category, Product, ProductImage, Order, OrderItem, Payment, Inventory, Cart, CartItem, Shipping, SubCategory

# Inline admin for OrderItem to display items within Order admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

# Admin for Order to handle order and inline items
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'user', 'status', 'total_amount', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email',)
    inlines = [OrderItemInline]

# Inline admin for CartItem to display items within Cart admin
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

# Admin for Cart to handle cart and inline items
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at')
    search_fields = ('user__email',)
    inlines = [CartItemInline]

# Admin for Shipping to handle shipping details
class ShippingAdmin(admin.ModelAdmin):
    list_display = ('order', 'address', 'city', 'postal_code', 'country', 'status', 'shipped_at')
    search_fields = ('order__user__email', 'city', 'country')
    list_filter = ('status', 'shipped_at')

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of extra forms to display for adding new images

# Admin for Product to manage products and related categories
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_id', 'name', 'category', 'price', 'available', 'created_at', 'updated_at')
    search_fields = ('name', 'category__name')
    list_filter = ('available', 'category')
    inlines = [ProductImageInline]  # Display ProductImage as an inline model

# Admin for Inventory to manage product stock
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'stock_quantity')
    search_fields = ('product__name',)

# Registering all models with their respective admins
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Shipping, ShippingAdmin)
