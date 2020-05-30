import cv2
from . import alignment, blend
import numpy as np
from scipy.special import comb


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
        float(25) * len(matches) / 100
    )

    if nMatches < 4:
        return None

    matches = matches[:nMatches]
    motionModel = 1
    nRANSAC = 600
    RANSACThreshold = 5

    return alignment.alignPair(
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

    step = smoothstep(np.linspace(0., blendWidth, blendWidth),
                      x_max=blendWidth, N=1)
    stepinv = step[::-1]
    alpha_x = np.concatenate((step,
                              np.ones(w - 2*blendWidth),
                              stepinv))
    alpha_y = np.concatenate((step,
                              np.ones(h - 2*blendWidth),
                              stepinv))
    alpha = np.outer(alpha_y, alpha_x)

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

    # Alpha blending
    right = np.dstack((right, np.ones(right.shape[:-1]))) * alpha_smooth(left.shape, blendWidth)
    left = np.dstack((left, np.ones(left.shape[:-1]))) * alpha_smooth(left.shape, blendWidth)

    warpedRightImage = cv2.warpPerspective(
        right, np.dot(translation, mapping), (newWidth, newHeight)
    )
    warpedLeftImage = cv2.warpPerspective(
        left, translation, (newWidth, newHeight)
    )

    # Alpha blending normalization
    dst = warpedLeftImage + warpedRightImage
    dst = blend.normalizeBlend(dst)
    dst = dst.astype(np.uint8)

    return dst
