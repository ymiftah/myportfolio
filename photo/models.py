import os
from django.db import models
from django.utils import timezone


# Create your models here.
class UpPhoto(models.Model):
    name = models.CharField(max_length=50)
    img_file = models.ImageField(
        upload_to='images/',
        verbose_name='Image File'
    )
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(UpPhoto, self).save(*args, **kwargs)
    