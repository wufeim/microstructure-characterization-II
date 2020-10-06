#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename: features.py
# @Date: 2020-06-21
# @Author: Wufei Ma

import cv2
import numpy as np

import mahotas.features
from skimage.feature import local_binary_pattern

# Kernels for opening and closing.
kernels = {}
kernels[3] = np.ones((3, 3), np.uint8)
kernels[5] = np.ones((5, 5), np.uint8)
kernels[7] = np.ones((7, 7), np.uint8)
kernels[9] = np.ones((9, 9), np.uint8)
kernels[11] = np.ones((11, 11), np.uint8)


def crop_image(image):
    """Crop margins from images with known sizes.
    """
    if image.shape[0] == 2048 and image.shape[1] == 2560:
        return image[:1920, :]
    elif image.shape[0] == 1428 and image.shape[1] == 2048:
        return image[:1408, :]
    elif image.shape[0] == 1024 and image.shape[1] == 1280:
        return image[:960, :]
    elif image.shape[0] == 1448 and image.shape[1] == 2048:
        return image[:1428, :]
    else:
        return image


def segmentation_feature(img, collectAreaFeatures, collectSpatialFeatures, d, sigma_color, sigma_space,
                         ksize0, ksize1, ksize2, ksize3):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_filtered = cv2.bilateralFilter(img, d, sigma_color, sigma_space)

    # Apply KMeans.
    Z = img_filtered.astype(np.float32).reshape((-1, 1))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1.0)
    ret, label, center = cv2.kmeans(Z, 2, None, criteria, 10, cv2.KMEANS_PP_CENTERS)

    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape(img.shape)

    # Apply closing then opening.
    p3 = np.array(res2, copy=True)
    p3[np.where(res2 != min(set(p3.flatten())))] = 255
    p3 = cv2.morphologyEx(p3, cv2.MORPH_CLOSE, kernels[ksize0])
    p3 = cv2.morphologyEx(p3, cv2.MORPH_OPEN, kernels[ksize1])
    p3_feature = np.sum(p3 != 255) / (img.shape[0] * img.shape[1])

    # Apply closing then opening.
    p2 = np.array(res2, copy=True)
    p2[np.where(p2 != min(set(p2.flatten())))] = 255
    p2 = cv2.morphologyEx(p2, cv2.MORPH_OPEN, kernels[ksize2])
    p2 = cv2.morphologyEx(p2, cv2.MORPH_CLOSE, kernels[ksize3])
    p2[np.where(p3 != 255)] = 255
    p2_feature = np.sum(p2 != 255) / (img.shape[0] * img.shape[1])

    area_features = np.expand_dims(np.array([1 - p2_feature - p3_feature, p2_feature, p3_feature]), 0)

    p2 = 255 - p2
    p3 = 255 - p3
    connectivity = 8
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(p2, connectivity, cv2.CV_32S)
    spatial_features = [
        num_labels - 1,
        np.mean(stats[1:, -1]),
        np.std(stats[1:, -1]),
        np.std(centroids[1:, 0]),
        np.std(centroids[1:, 1]),
        np.mean(stats[1:, 2] * stats[1:, 3] / stats[1:, 4]),
        np.std(stats[1:, 2] * stats[1:, 3] / stats[1:, 4])
    ]

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(p3, connectivity, cv2.CV_32S)
    spatial_features += [
        num_labels - 1,
        np.mean(stats[1:, -1]),
        np.std(stats[1:, -1]),
        np.std(centroids[1:, 0]),
        np.std(centroids[1:, 1]),
        np.mean(stats[1:, 2] * stats[1:, 3] / stats[1:, 4]),
        np.std(stats[1:, 2] * stats[1:, 3] / stats[1:, 4])
    ]

    spatial_features = np.expand_dims(np.array(spatial_features), 0)

    if collectAreaFeatures and collectSpatialFeatures:
        return np.hstack((area_features, spatial_features))
    elif collectAreaFeatures:
        return area_features
    elif collectSpatialFeatures:
        return spatial_features
    else:
        return None


def haralick_feature(img, distance):
    if img is None:
        return np.zeros((1, 13))
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h = mahotas.features.haralick(img_rgb, distance=distance, return_mean=True, ignore_zeros=False)
    return np.expand_dims(h, 0)


def lbp_feature(img, P, R):
    if img is None:
        return np.zeros((1, 12))
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lbp = local_binary_pattern(img_rgb, P=P, R=R)
    f, _ = np.histogram(lbp, bins=P+2, range=(0, P+2), density=True)
    return np.expand_dims(f, 0)


def collect_features(img, collectAreaFeatures, collectSpatialFeatures, collectHaralickFeatures, collectLBPFeatures,
                     distance=1, P=10, R=5, d=15, sigma_color=75, sigma_space=75,
                     ksize0=9, ksize1=9, ksize2=9, ksize3=3):
    img = crop_image(img)

    features = None

    if collectAreaFeatures or collectSpatialFeatures:
        f = segmentation_feature(img, collectAreaFeatures, collectSpatialFeatures, d=d, sigma_color=sigma_color,
                                 sigma_space=sigma_space, ksize0=ksize0, ksize1=ksize1, ksize2=ksize2, ksize3=ksize3)
        if features is None:
            features = f
        else:
            features = np.hstack((features, f))

    if collectHaralickFeatures:
        f = haralick_feature(img, distance=distance)
        if features is None:
            features = f
        else:
            features = np.hstack((features, f))

    if collectLBPFeatures:
        f = lbp_feature(img, P, R)
        if features is None:
            features = f
        else:
            features = np.hstack((features, f))

    return features


if __name__ == '__main__':
    img = cv2.imread('/Users/wufeim/Documents/images/DUM1142 002 500X 30keV HC14 Center LBE 002.tif')
    img = crop_image(img)
    f = segmentation_feature(img, True, True, d=15, sigma_color=75, sigma_space=75)
    print(f.shape)
