from django.contrib import admin

from .models import UserCurrentPosition, Group

# Register your models here.
admin.site.register(UserCurrentPosition)
admin.site.register(Group)
