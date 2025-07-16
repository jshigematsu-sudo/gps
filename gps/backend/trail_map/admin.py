from django.contrib import admin

from .models import Location, RequestLog

admin.site.register(Location)
admin.site.register(RequestLog)
# Register your models here.
