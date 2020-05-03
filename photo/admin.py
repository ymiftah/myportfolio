from django.contrib import admin

# Register your models here.
from .models import PhotoModel  # ,  DistortPhotoModel


class PhotoAdmin(admin.ModelAdmin):
    # ...
    list_display = ('img_file', 'created')


# class DistortPhotoAdmin(admin.ModelAdmin):
#     # ...
#     list_display = ('img_file', 'f', 'k1', 'k2', 'created')


admin.site.register(PhotoModel, PhotoAdmin)
# admin.site.register(DistortPhotoModel, DistortPhotoAdmin)
