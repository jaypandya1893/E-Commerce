from django.contrib import admin
from .models import User,Product,Wishlist,Cart,Transaction

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Wishlist)
admin.site.register(Cart)
admin.site.register(Transaction)