from shop.models.utils import *
import random
from accounts.models.user_models import User
from django.db.models import Avg


class Product(models.Model):
    product_id = models.CharField(max_length=8, unique=True, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    description = models.TextField()
    regular_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    sizes = models.JSONField(null=True, blank=True)
    colors = models.JSONField(null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    sub_category = models.ForeignKey('SubCategory', on_delete=models.SET_NULL, null=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    product_code = models.CharField(max_length=50, null=True, blank=True)
    product_sku = models.CharField(max_length=50, null=True, blank=True)
    tags = models.JSONField(null=True, blank=True)
    quantity = models.IntegerField(default=0)
    in_stock = models.BooleanField(default=True)
    status = models.BooleanField(default=True)
    liked_by = models.ManyToManyField(User, related_name='liked_products', blank=True)
    top_collection = models.BooleanField(default=False)
    average_rating = models.FloatField(default=0.0)
    best_seller = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    def generate_unique_id(self):
        while True:
            product_id = random.randint(10000000, 99999999)
            if not Product.objects.filter(product_id=product_id).exists():
                return product_id
            
    def update_average_rating(self):
        """
        Updates the average rating of the product based on its reviews.
        """
        avg_rating = self.reviews.aggregate(Avg('rating'))['rating__avg']
        self.average_rating = avg_rating if avg_rating else 0.0
        self.save()
            
    def save(self, *args, **kwargs):
        if not self.product_id:
            self.product_id = self.generate_unique_id()
        if not self.slug:
            self.slug = slugify(self.name)

        # Set in_stock based on quantity
        self.in_stock = self.quantity > 0

        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'Image for {self.product.name}'
    


class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    stock_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.product.name} - {self.stock_quantity} items in stock'
