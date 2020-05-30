from io import BytesIO
from django.core.files import File
from PIL import Image

import numpy as np
import cv2

from .blend import *
from .alignment import *
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.special import comb

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


def img_features(image, params=[1]):
    # unzip parameters
    tol = float(params[0])

    img = Image.open(image)
    img = np.array(img)
    img2 = img * 0

    # ORB detector
    orb = cv2.ORB_create()
    # find the keypoints with ORB
    kp = orb.detect(img, None)
    # compute the descriptors with ORB
    kp, des = orb.compute(img, kp)
    last_idx = int(tol * len(kp))
    kp, des = kp[:last_idx], des[:last_idx]

    # draw only keypoints location, not size and orientation
    cv2.drawKeypoints(img, kp, img2, color=(0, 255, 0), flags=0)
    img2 = Image.fromarray(img2)

    return img2


def img_features_matcher(image1, image2, params=[15]):
    # unzip parameters
    num = int(params[0])

    img1 = Image.open(image1)
    img1 = np.array(img1)

    img2 = Image.open(image2)
    img2 = np.array(img2)

    # ORB detector
    orb = cv2.ORB_create()
    # find the keypoints with ORB
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    # create BFMatcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # Match descriptors.
    matches = bf.match(des1, des2)
    # Sort them in the order of their distance.
    matches = sorted(matches, key=lambda x: x.distance)
    # Make sure num is within bounds
    num = min(num, len(matches))
    # Draw first n matches.
    img3 = img1 * 0
    img3 = cv2.drawMatches(img1, kp1, img2, kp2, matches[:num], img3, flags=2)

    img3 = Image.fromarray(img3)

    return img3


def img_stitcher(image1, image2, params=[30]):
    def computeMapping(leftImage, rightImage):
        leftGrey = cv2.cvtColor(leftImage, cv2.COLOR_BGR2GRAY)
        rightGrey = cv2.cvtColor(rightImage, cv2.COLOR_BGR2GRAY)
        orb = cv2.ORB_create()
        leftKeypoints, leftDescriptors = orb.detectAndCompute(leftGrey, None)
        rightKeypoints, rightDescriptors = orb.detectAndCompute(
            rightGrey, None
        )
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(leftDescriptors, rightDescriptors)
        matches = sorted(matches, key=lambda x: x.distance)

        nMatches = int(
            float(30) * len(matches) / 100
        )

        if nMatches < 4:
            return None

        matches = matches[:nMatches]
        motionModel = 1
        nRANSAC = 600
        RANSACThreshold = 5

        return alignPair(
            leftKeypoints, rightKeypoints, matches,
            motionModel, nRANSAC, RANSACThreshold
        )


    def alpha_smooth(shape, blendWidth):
        h, w, _ = shape

        def smoothstep(x, x_min=0, x_max=1, N=4):
            x = np.clip((x - x_min) / (x_max - x_min), 0, 1)

            result = 0
            for n in range(0, N + 1):
                result += comb(N + n, n) * comb(2 * N + 1, N - n) * (-x) ** n

            result *= x ** (N + 1)

            return result
        
        if min(h, w) < 2 * blendWidth:
            blendWidth = int(min(h, w) / 2 - 1)
        step = smoothstep(np.linspace(0., blendWidth, blendWidth), x_max=blendWidth, N=1)
        stepinv = step[::-1]
        alpha_x = np.concatenate((step,
                                np.ones(w - 2*blendWidth),
                                stepinv))
        alpha_y = np.concatenate((step,
                                np.ones(h - 2*blendWidth),
                                stepinv))
        alpha = np.outer(alpha_y, alpha_x)
        #alpha = gaussian_filter(alpha, sigma=blendWidth, mode='nearest') * alpha
        return np.dstack([alpha, alpha, alpha, alpha])

    def compute(left, right, blendWidth=20, *args):
        mapping = computeMapping(right, left)
        height, width, _ = right.shape

        points = np.array([
            [0, 0, 1],
            [width, 0, 1],
            [0, height, 1],
            [width, height, 1],
        ], dtype=float)
        trans_points = np.dot(mapping, points.T).T
        trans_points = trans_points / trans_points[:, 2][:, np.newaxis]

        all_points = np.vstack([points, trans_points])

        minX = np.min(all_points[:, 0])
        maxX = np.max(all_points[:, 0])
        minY = np.min(all_points[:, 1])
        maxY = np.max(all_points[:, 1])

        # Create an accumulator image
        newWidth = int(np.ceil(maxX) - np.floor(minX))
        newHeight = int(np.ceil(maxY) - np.floor(minY))

        translation = np.array([[1, 0, -minX], [0, 1, -minY], [0, 0, 1]])

        right = right * .5 # np.dstack((right, np.ones(right.shape[:-1]))) * alpha_smooth(left.shape, blendWidth)
        left = left * .5 # np.dstack((left, np.ones(left.shape[:-1]))) * alpha_smooth(left.shape, blendWidth)

        warpedRightImage = cv2.warpPerspective(
            right, np.dot(translation, mapping), (newWidth, newHeight)
        )
        warpedLeftImage = cv2.warpPerspective(
            left, translation, (newWidth, newHeight)
        )

        ## Alpha blending
        dst = warpedLeftImage + warpedRightImage
        #dst = normalizeBlend(dst)
        dst = dst.astype(np.uint8)

        return dst

    blendWidth = int(params[0])

    img1 = Image.open(image1)
    img1 = np.array(img1)

    img2 = Image.open(image2)
    img2 = np.array(img2)

    img3 = compute(img1, img2, blendWidth=blendWidth)
    img3 = Image.fromarray(img3)

    return img3
