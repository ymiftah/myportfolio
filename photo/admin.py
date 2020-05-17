from django.contrib import admin

# Register your models here.
from .models import PhotoModel, PhotoFolderModel  # ,  DistortPhotoModel


class PhotoAdmin(admin.ModelAdmin):
    # ...
    list_display = ('folder', 'img_file', 'created')


class PhotoFolderAdmin(admin.ModelAdmin):
    # ...
    list_display = ('name', 'description')


admin.site.register(PhotoFolderModel, PhotoFolderAdmin)
admin.site.register(PhotoModel, PhotoAdmin)
