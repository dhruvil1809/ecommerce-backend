from shop.models.utils import *
import random
from accounts.models.user_models import User
from django.db.models import Avg
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Tag(models.Model):
    var_title = models.CharField(max_length=255)
    deleted = models.BooleanField(default=False)

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.save()

    def __str__(self):
        return self.var_title

class Attribute(models.Model):
    var_title = models.CharField(max_length=255)
    deleted = models.BooleanField(default=False)

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.save()

    def __str__(self):
        return self.var_title
    
    
class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, related_name='values', on_delete=models.CASCADE)
    var_title = models.CharField(max_length=255)
    color_code = models.CharField(max_length=255,blank=True, null=True)
    deleted = models.BooleanField(default=False)

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.save()

    def __str__(self):
        return f"{self.attribute.var_title}: {self.var_title}"
    
    
class Product(models.Model):
    product_id = models.CharField(max_length=8, unique=True, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    sub_category = models.ForeignKey('SubCategory', on_delete=models.SET_NULL, null=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='products', blank=True)
    in_stock = models.BooleanField(default=True)
    status = models.BooleanField(default=True)
    has_variants = models.BooleanField(default=False)
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
        self.average_rating = round(avg_rating, 1) if avg_rating else 0.0
        self.save()
            
    def save(self, *args, **kwargs):
        if not self.product_id:
            self.product_id = self.generate_unique_id()
        self.slug = slugify(self.name)

        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Variant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    product_code = models.CharField(max_length=50, null=True, blank=True)
    product_sku = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    product_details = models.JSONField(blank=True, null=True)
    product_descriptions = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.name}"
    
    
class VariantAttribute(models.Model):
    variant = models.ForeignKey(Variant, related_name='variant_attributes', on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, related_name='variant_attributes', on_delete=models.CASCADE)
    value = models.ForeignKey(AttributeValue, related_name='variant_values', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.variant} - {self.attribute.var_title}: {self.value.var_title}"


class VariantImage(models.Model):
    variant = models.ForeignKey(Variant,related_name='variant_images',on_delete=models.CASCADE)
    image = models.ImageField(upload_to='variants/')
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'Image for {self.variant}'
    


# Signal to update `in_stock` field in Product when Inventory changes
# @receiver(post_save, sender=Inventory)
# @receiver(post_delete, sender=Inventory)
# def update_product_in_stock(sender, instance, **kwargs):
#     product = instance.product
#     total_quantity = product.inventory.aggregate(total=models.Sum('quantity'))['total']
#     product.in_stock = total_quantity > 0 if total_quantity else False
#     product.save()