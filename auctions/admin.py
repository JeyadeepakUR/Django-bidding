from django.contrib import admin

from .models import Category, Listing, Bid, Comment

admin.site.register(Category)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)
