from django.contrib import admin

# Register your models here.
from .models import *

class UpPhotoAdmin(admin.ModelAdmin):
    # ...
    list_display = ('name', 'img_file', 'created')

admin.site.register(UpPhoto, UpPhotoAdmin)
