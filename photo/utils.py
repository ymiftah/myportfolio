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

    X, Y = im.size
    XX, YY = IMG_SIZE
    new_size = (YY * X // Y, YY)
    resized = im.resize(new_size)  # resize image

    thumb_io = BytesIO()  # create a BytesIO object
    resized.save(thumb_io, 'PNG')  # save image to BytesIO object
    # create a django friendly File object
    thumbnail = File(thumb_io, name="thumb" + image.name)
    return thumbnail
