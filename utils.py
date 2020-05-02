#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename : utils.py
# @Date : 2020-05-03
# @Author : Wufei Ma

import os
import sys

import cv2
import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
plt.rcParams['axes.grid'] = False

from sklearn import cluster
from scipy.ndimage.filters import median_filter, gaussian_filter

import features

COLORS = [(219, 94, 86),
          (86, 219, 127),
          (86, 111, 219)]

def format_time(time):
    time = int(time)
    if time < 60:
        return '{:d}s'.format(time)
    elif 60 <= time < 3600:
        return '{:d}m {:d}s'.format(time // 60, time % 60)
    elif 3600 <= time:
        return '{:d}h {:d}m {:d}s'.format(time // 3600,
                                          (time % 3600) // 60, time % 60)


def crop_image(image):

    if image.shape[0] == 2048 and image.shape[1] == 2560:
        return image[:1920, :]
    elif image.shape[0] == 1428 and image.shape[1] == 2048:
        return image[:1408, :]
    elif image.shape[0] == 1024 and image.shape[1] == 1280:
        return image[:960, :]
    elif image.shape[0] == 1448 and image.shape[1] == 2048:
        return image[:1428, :]
    else:
        raise Exception("Unknown image size: {}".format(image.shape))


def segment_image(image_name, d=15, sigma_color=75, sigma_space=75):
    _, seg_img = features.segmentation(image_name, d, sigma_color, sigma_space,
                                       visualization=True)
    return seg_img


if __name__ == '__main__':

    pass
