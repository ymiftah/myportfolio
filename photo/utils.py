from io import BytesIO
from django.core.files import File
from PIL import Image

import numpy as np
import cv2


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


def img_distort(image, params=[500, -0.3, 0.3], return_img='True'):
    # helper function to distort the grid
    def transform_lens_distortion(shape, f=500, k1=-0.3, k2=0.3):
        h, w = shape

        # Center coordinates of image
        x = np.linspace(-w/2, w/2, w)
        y = np.linspace(-h/2, h/2, h)
        xf, yf = np.meshgrid(x, y)

        # Divide by focal
        xf /= f
        yf /= f

        # compute the Euclidean coordinates of the sphere
        xt = np.sin(xf) * np.cos(yf)
        yt = np.sin(yf)
        zt = np.cos(xf) * np.cos(yf)

        # Project the points to the z=1 plane at (xt/zt,yt/zt,1),
        xn = xt / (zt + 1e-6)  # 1e-6 in case of zero division
        yn = yt / (zt + 1e-6)  # 1e-6 in case of zero division

        # distort with radial distortion coefficients k1 and k2
        r2 = xn*xn + yn*yn
        xt = xn * (1 + k1 * r2 + k2 * r2**2)
        yt = yn * (1 + k1 * r2 + k2 * r2**2)

        # Multiply by focal and center
        xn = (xt * f) + .5 * w
        yn = (yt * f) + .5 * h

        # Stack in a transformation matrix (x, y) --> (u, v)
        # uv[x, y, 0] = u
        # uv[x, y, 1] = v
        uv = np.dstack((xn, yn))

        return uv

    # unzip parameters
    f, k1, k2 = map(float, params)

    img = Image.open(image)

    img = np.array(img)

    # image size
    h, w, _ = img.shape

    # Get the transformation
    uv = transform_lens_distortion(img.shape[:2], f, k1, k2)

    # Warp image
    warped = cv2.remap(
        img,
        uv[:, :, 0].astype(np.float32),
        uv[:, :, 1].astype(np.float32),
        cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE
        )

    # define a mask to filter the interpolation remnants
    mask = cv2.inRange(uv[:, :, 1], 0, h-1) & cv2.inRange(uv[:, :, 0], 0, w-1)

    # Apply mask
    img2 = cv2.bitwise_and(warped, warped, mask=mask)
    img2 = Image.fromarray(img2)

    if return_img:
        return img2

    thumb_io = BytesIO()  # create a BytesIO object

    img2.save(thumb_io, 'PNG')  # save image to BytesIO object

    # create a django friendly File object
    return File(thumb_io, name="distort" + image.name)
