from io import BytesIO
from django.core.files import File
from PIL import Image

IMG_SIZE = 1080, 720


def img_resize(image, size=IMG_SIZE):
    """ Resize image on the Fly"""
    # Open Image
    im = Image.open(image)
    # convert mode if jpg file
    if image.name.endswith('jpg'):
        im.convert('RGB')

    im.thumbnail(IMG_SIZE)  # resize image

    thumb_io = BytesIO()  # create a BytesIO object
    im.save(thumb_io, 'PNG')  # save image to BytesIO object
    thumbnail = File(thumb_io, name="thumb"+ image.name)  # create a django friendly File object
    return thumbnail
