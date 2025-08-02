from django.db import models
from category.models import Category
from django.urls import reverse

# Create your models here.

class Product(models.Model):
    company_name    = models.CharField(max_length=100, default='Vogona')
    product_name    = models.CharField(max_length=100, unique=True)
    slug            = models.SlugField(max_length=100, unique=True)
    discription     = models.TextField(max_length=500, blank=True)
    price           = models.IntegerField()
    images          = models.ImageField(upload_to='product_images')
    stock           = models.IntegerField()
    is_available    = models.BooleanField(default=True)
    category        = models.ForeignKey(Category, on_delete=models.CASCADE)
    create_date     = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now_add=True)


    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])


    def __str__(self):
        return self.product_name

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)

class Variation(models.Model):
    VARIATION_CATEGORIES = [
        ('color', 'Color'),
        ('size', 'Size'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=20, choices=VARIATION_CATEGORIES)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    objects =VariationManager()

    def __str__(self):
        return self.variation_value