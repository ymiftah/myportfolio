from django.db import models
from django.utils import timezone
from .utils import img_resize, img_distort


# Create your models here.
class PhotoModel(models.Model):
    img_file = models.ImageField(
        upload_to='images/',
        verbose_name='Image File'
    )
    thumbnail = models.ImageField(
        upload_to='thumbnails/',
        verbose_name='Thumbnail File')
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        # Resize
        self.thumbnail = img_resize(self.img_file)
        return super(PhotoModel, self).save(*args, **kwargs)


# class DistortPhotoModel(models.Model):
#     # Model attributes
#     distorted = models.ImageField(
#         upload_to='distortion/',
#         verbose_name='Thumbnail File',
#         blank=True,
#         )
#     created = models.DateTimeField(editable=False)
#     modified = models.DateTimeField()
#     img_file = models.ForeignKey(PhotoModel, on_delete=models.CASCADE)

#     # transformation parameters
#     f = models.FloatField()
#     k1 = models.FloatField()
#     k2 = models.FloatField()

#     # Override save method
#     def save(self, *args, **kwargs):
#         ''' On save, update timestamps '''
#         if not self.id:
#             self.created = timezone.now()
#         self.modified = timezone.now()

#         # Distort

#         self.distorted = img_distort(self.img_file.img_file,
#                                      [self.f, self.k1, self.k2])
#         return super(DistortPhotoModel, self).save(*args, **kwargs)
