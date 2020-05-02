#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Filename : features.py
# @Date : 2019-09-13
# @Author : Mofii

from __future__ import absolute_import

import os
import sys

import numpy as np
import cv2
import seaborn as sns
from matplotlib import pyplot as plt

import mahotas.features
from sklearn import cluster
from skimage.feature import local_binary_pattern
from scipy.ndimage.filters import median_filter, gaussian_filter

import utils

# Set Matplotlib and Seaborn params
rc = {"axes.spines.left" : False,
      "axes.spines.right" : False,
      "axes.spines.bottom" : False,
      "axes.spines.top" : False,
      "xtick.bottom" : False,
      "xtick.labelbottom" : False,
      "ytick.labelleft" : False,
      "ytick.left" : False}
plt.rcParams.update(rc)
sns.set_style('whitegrid', {'axes.grid': False})


# Kernels for opening and closing.
kernel3 = np.ones((3, 3), np.uint8)
kernel5 = np.ones((5, 5), np.uint8)
kernel7 = np.ones((7, 7), np.uint8)
kernel9 = np.ones((9, 9), np.uint8)
kernel11 = np.ones((11, 11), np.uint8)


def haralick_features(image_names, distance=1):
    f = []
    for i in range(len(image_names)):
        img = cv2.imread(image_names[i])
        img = utils.crop_image(img)
        if img is None or img.size == 0 or np.sum(img[:]) == 0 or img.shape[0] == 0 or img.shape[1] == 0:
            h = np.zeros((1, 13))
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h = mahotas.features.haralick(img, distance=distance, return_mean=True, ignore_zeros=False)
            h = np.expand_dims(h, 0)
        if i == 0:
            f = h
        else:
            f = np.vstack((f, h))
    return f


def lbp_features(image_names, P=10, R=5):
    f = []
    for i in range(len(image_names)):
        img = cv2.imread(image_names[i])
        img = utils.crop_image(img)
        if img is None or img.size == 0 or np.sum(img[:]) == 0 or img.shape[0] == 0 or img.shape[1] == 0:
            h = np.zeros((1, 13))
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            lbp = local_binary_pattern(img, P=P, R=R)
            # h, _ = np.histogram(lbp, normed=True, bins=P + 2, range=(0, P + 2))
            h, _ = np.histogram(lbp, bins=P+2, range=(0, P+2), density=True)
        if i == 0:
            f = h
        else:
            f = np.vstack((f, h))
    return f


def spatial(image_name, d=15, sigma_color=75, sigma_space=75):
    img = cv2.imread(image_name, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError("Image {:s} cannot be opened."
                                .format(image_name))

    # Pre-process the images.
    img = utils.crop_image(img)
    img = cv2.bilateralFilter(img, d, sigma_color, sigma_space)

    # Apply KMeans.
    Z = img.astype(np.float32).reshape((-1, 1))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1.0)
    ret, label, center = cv2.kmeans(Z, 2, None, criteria, 10,
                                    cv2.KMEANS_PP_CENTERS)
    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape(img.shape)

    # Apply closing then opening.
    p3 = np.array(res2, copy=True)
    p3[np.where(res2 != min(set(p3.flatten())))] = 255
    p3 = cv2.morphologyEx(p3, cv2.MORPH_CLOSE, kernel9)
    p3 = cv2.morphologyEx(p3, cv2.MORPH_OPEN, kernel9)

    # Apply closing then opening.
    p2 = np.array(res2, copy=True)
    p2[np.where(p2 != min(set(p2.flatten())))] = 255
    p2 = cv2.morphologyEx(p2, cv2.MORPH_OPEN, kernel9)
    p2 = cv2.morphologyEx(p2, cv2.MORPH_CLOSE, kernel3)
    p2[np.where(p3 != 255)] = 255

    p2 = 255 - p2
    p3 = 255 - p3

    connectivity = 8
    num_labels, labels, stats, centroids = \
        cv2.connectedComponentsWithStats(p2, connectivity, cv2.CV_32S)
    f = [
        num_labels - 1,             # number of regions                 0
        np.mean(stats[1:, -1]),     # mean of region areas              1
        np.std(stats[1:, -1]),      # std of region areas               2
        np.std(centroids[1:, 0]),   # std of the x-axis of centroid     3
        np.std(centroids[1:, 1]),   # std of the y-axis of centroids    4
        # mean and std of (width * height / area)
        np.mean(stats[1:, 2] * stats[1:, 3] / stats[1:, 4]),          # 5
        np.std(stats[1:, 2] * stats[1:, 3] / stats[1:, 4])            # 6
    ]

    connectivity = 8
    num_labels, labels, stats, centroids = \
        cv2.connectedComponentsWithStats(p3, connectivity, cv2.CV_32S)
    f += [
        num_labels - 1,  # number of regions                            7
        np.mean(stats[1:, -1]),  # mean of region areas                 8
        np.std(stats[1:, -1]),  # std of region areas                   9
        np.std(centroids[1:, 0]),  # std of the x-axis of centroid     10
        np.std(centroids[1:, 1]),  # std of the y-axis of centroids    11
        # mean and std of (width * height / area)
        np.mean(stats[1:, 2] * stats[1:, 3] / stats[1:, 4]),         # 12
        np.std(stats[1:, 2] * stats[1:, 3] / stats[1:, 4])           # 13
    ]
    return f


def spatial_features(image_names, d=15, sigma_color=75, sigma_space=75):
    features = []
    for i in image_names:
        try:
            feature = spatial(i, d, sigma_color, sigma_space)
        except FileNotFoundError as e:
            print("File not found ({}): {}".format(e.errno, e.strerror))
            continue
        if len(features) == 0:
            features = feature
        else:
            features = np.vstack((features, feature))

    return features


def segmentation(image_name, d=15, sigma_color=75, sigma_space=75,
                     visualization=True):
    img = cv2.imread(image_name, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError("Image {:s} cannot be opened."
                                .format(image_name))

    # Pre-process the images.
    img = utils.crop_image(img)
    img = cv2.bilateralFilter(img, d, sigma_color, sigma_space)

    # Apply KMeans.
    Z = img.astype(np.float32).reshape((-1, 1))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1.0)
    ret, label, center = cv2.kmeans(Z, 2, None, criteria, 10,
                                    cv2.KMEANS_PP_CENTERS)
    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape(img.shape)

    # Apply closing then opening.
    p3 = np.array(res2, copy=True)
    p3[np.where(res2 != min(set(p3.flatten())))] = 255
    p3 = cv2.morphologyEx(p3, cv2.MORPH_CLOSE, kernel9)
    p3 = cv2.morphologyEx(p3, cv2.MORPH_OPEN, kernel9)
    p3_feature = np.sum(p3 != 255) / (img.shape[0]*img.shape[1])

    # Apply closing then opening.
    p2 = np.array(res2, copy=True)
    p2[np.where(p2 != min(set(p2.flatten())))] = 255
    p2 = cv2.morphologyEx(p2, cv2.MORPH_OPEN, kernel9)
    p2 = cv2.morphologyEx(p2, cv2.MORPH_CLOSE, kernel3)
    p2[np.where(p3 != 255)] = 255
    p2_feature = np.sum(p2 != 255) / (img.shape[0]*img.shape[1])

    features = np.asarray([1 - p2_feature - p3_feature, p2_feature, p3_feature])

    if visualization:
        colors = [(219, 94, 86),
                  (86, 219, 127),
                  (86, 111, 219)]
        seg_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.int32)
        seg_img[(p2 == 255) * (p3 == 255)] = colors[0]
        seg_img[p2 != 255] = colors[1]
        seg_img[p3 != 255] = colors[2]
        return features, seg_img
    else:
        return features


def area_features(image_names, d=15, sigma_color=75, sigma_space=75):
    features = []
    for i in image_names:
        try:
            feature = segmentation(i, d, sigma_color, sigma_space,
                                   visualization=False)
        except FileNotFoundError as e:
            print("File not found ({}): {}".format(e.errno, e.strerror))
            continue
        if len(features) == 0:
            features = feature
        else:
            features = np.vstack((features, feature))

    return features


if __name__ == '__main__':

    pass
