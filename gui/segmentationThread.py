#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename: segmentationThread.py
# @Date: 2020-06-21
# @Author: Wufei Ma

import os
import cv2
import numpy as np

from PyQt5.QtCore import pyqtSignal, QThread

from features import crop_image

colors = [(219, 94, 86),
          (86, 219, 127),
          (86, 111, 219)]

# Kernels for opening and closing.
kernel3 = np.ones((3, 3), np.uint8)
kernel5 = np.ones((5, 5), np.uint8)
kernel7 = np.ones((7, 7), np.uint8)
kernel9 = np.ones((9, 9), np.uint8)
kernel11 = np.ones((11, 11), np.uint8)


class SegmentationThread(QThread):

    succeed_signal = pyqtSignal()
    fail_signal = pyqtSignal(str)

    def __init__(self, imageFilename, outputPath, d=15, sigma_color=75, sigma_space=75):
        QThread.__init__(self)
        self.imageFilename = imageFilename
        self.outputPath = outputPath
        self.d = d
        self.sigma_color = sigma_color
        self.sigma_space = sigma_space

        self.img = None

        self.running = True

    def __del__(self):
        self.wait()

    def run(self):
        self.running = True

        img = cv2.imread(self.imageFilename, cv2.IMREAD_GRAYSCALE)
        if img is None:
            self.fail_signal.emit('Failed to load image: {:s}'.format(self.imageFilename))
        img = crop_image(img)

        img = cv2.bilateralFilter(img, self.d, self.sigma_color, self.sigma_space)
        Z = img.astype(np.float32).reshape((-1, 1))
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1.0)
        ret, label, center = cv2.kmeans(Z, 2, None, criteria, 10, cv2.KMEANS_PP_CENTERS)

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

        seg_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        seg_img[(p2 == 255) * (p3 == 255)] = colors[0]
        seg_img[p2 != 255] = colors[1]
        seg_img[p3 != 255] = colors[2]
        seg_img = cv2.cvtColor(seg_img, cv2.COLOR_BGR2RGB)

        basename = '.'.join(os.path.basename(self.imageFilename).split('.')[:-1])
        self.outputFilename = os.path.join(self.outputPath, basename+'_segmentation.png')
        if self.running:
            cv2.imwrite(self.outputFilename, seg_img)
            self.succeed_signal.emit()

    def stop(self):
        self.running = False
