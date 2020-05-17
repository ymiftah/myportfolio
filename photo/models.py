from django.db import models
from django.utils import timezone
# from .utils import img_resize, img_distort


def get_path(instance, filename):
    return '{0}/{1}'.format(instance.folder.name, filename)


# Create your models here.
class PhotoFolderModel(models.Model):
    name = models.CharField(verbose_name="Folder name", max_length=120)
    description = models.TextField(verbose_name='Description of the folder')

    def __str__(self):
        return self.name


class PhotoModel(models.Model):
    folder = models.ForeignKey(PhotoFolderModel, on_delete=models.CASCADE)
    img_file = models.ImageField(
        upload_to=get_path,
        verbose_name='Image File'
    )
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        # Resize
        # self.thumbnail = img_resize(self.img_file)
        return super(PhotoModel, self).save(*args, **kwargs)

    def delete(self):
        self.img_file.delete()
        super(PhotoModel, self).delete()
