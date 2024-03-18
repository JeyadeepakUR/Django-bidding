from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Category(models.Model): # represent category of listings
    
    category = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.category}"

class Listing(models.Model):

    CATEGORY_CHOICES = [
        ('Fashion', 'Fashion'),
        ('Toys', 'Toys'),
        ('Electronics', 'Electronics'),
        ('Home', 'Home'),
        ('Other', 'Other')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings') # user who posted the listing
    title = models.CharField(max_length=64)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listing_category")
    categories = models.CharField(max_length=64, choices=CATEGORY_CHOICES, default="Other") # all categories to select from
    image_url = models.URLField(default='google.com')
    sold = models.BooleanField(default=False)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='won_listings')

    def __str__(self):
        return f"{self.title} posted by {self.user}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    price = models.DecimalField(default = 0.0, max_digits=6, decimal_places=2)
    
    def __str__(self):
        return f"bid on item: {self.listing} by {self.user} with price: {self.price}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return f"{self.comment} - {self.user}"

class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    watching = models.BooleanField(default=False)