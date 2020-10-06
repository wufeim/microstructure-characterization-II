#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename: featureCollectionThread.py
# @Date: 2020-06-21
# @Author: Wufei Ma

import os
import pandas as pd
from PyQt5.QtCore import pyqtSignal, QThread

from features import *


class FeatureCollectionThread(QThread):

    incremental_signal = pyqtSignal()
    output_signal = pyqtSignal(str)
    complete_signal = pyqtSignal()

    def __init__(self, filenames, collectAreaFeatures, collectSpatialFeatures, collectHaralickFeatures,
                 collectLBPFeatures, outputFilename, params):
        QThread.__init__(self)
        self.filenames = filenames
        self.collectAreaFeatures = collectAreaFeatures
        self.collectSpatialFeatures = collectSpatialFeatures
        self.collectHaralickFeatures = collectHaralickFeatures
        self.collectLBPFeatures = collectLBPFeatures
        self.outputFilename = outputFilename
        self.distance = params['distance']
        self.P = params['P']
        self.R = params['R']
        self.d = params['d']
        self.sigma_color = params['sigma_color']
        self.sigma_space = params['sigma_space']
        self.ksize0 = params['ksize0']
        self.ksize1 = params['ksize1']
        self.ksize2 = params['ksize2']
        self.ksize3 = params['ksize3']

        self.features = None

        self.running = True

    def __del__(self):
        self.wait()

    def save_features(self, features):
        columns = []
        if self.collectAreaFeatures:
            for i in range(3):
                columns.append('area_{:d}'.format(i))
        if self.collectSpatialFeatures:
            for i in range(14):
                columns.append('spatial_{:d}'.format(i))
        if self.collectHaralickFeatures:
            for i in range(13):
                columns.append('haralick_{:d}'.format(i))
        if self.collectLBPFeatures:
            for i in range(12):
                columns.append('lbp_{:d}'.format(i))
        df = pd.DataFrame(data=features, columns=columns)

        basenames = [os.path.basename(x) for x in self.filenames]
        df.insert(0, 'filename', value=basenames)

        df.to_csv(self.outputFilename)

    def run(self):
        self.running = True

        self.output_signal.emit('Feature collection thread ready.')

        features = None
        for i, fname in enumerate(self.filenames):
            if not self.running:
                return None
            img = cv2.imread(fname)
            if img is None:
                self.incremental_signal.emit()
                self.output_signal.emit('Failed to load image: {:s}'.format(fname))
                continue
            f = collect_features(img, self.collectAreaFeatures, self.collectSpatialFeatures,
                                 self.collectHaralickFeatures, self.collectLBPFeatures,
                                 distance=self.distance, P=self.P, R=self.R, d=self.d, sigma_color=self.sigma_color,
                                 sigma_space=self.sigma_space, ksize0=self.ksize0, ksize1=self.ksize1,
                                 ksize2=self.ksize2, ksize3=self.ksize3)
            if features is None:
                features = f
            else:
                features = np.vstack((features, f))

            self.incremental_signal.emit()
            # self.output_signal.emit('Complete one.')

        if self.running:
            self.save_features(features)

            self.output_signal.emit('Completed! Collected features of shape {} exported to {:s}.'
                                    .format(features.shape, self.outputFilename))
            self.incremental_signal.emit()
            self.complete_signal.emit()

    def stop(self):
        self.running = False
