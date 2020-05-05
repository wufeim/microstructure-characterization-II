#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename : utils.py
# @Date : 2020-05-03
# @Author : Wufei Ma

import os
import sys
import itertools

import cv2
import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
plt.rcParams['axes.grid'] = False

import features

COLORS = [(219, 94, 86),
          (86, 219, 127),
          (86, 111, 219)]
cols = ['HT1-C1', 'HT1-C2', 'HT1-C3', 'HT1-C4', 'HT1-C5', 'HT1-C6',
        'HT2-C1', 'HT2-C3', 'HT2-C4', 'HT2-C5']


class Logger(object):

    def __init__(self, filename):
        self.str = ''
        self.filename = filename

    def log(self, str):
        self.str += str + '\n'
        print(str)

    def flush(self):
        with open(self.filename, 'w') as f:
            f.write(self.str)
            f.close()


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


def segment_image(img, d=15, sigma_color=75, sigma_space=75):
    if len(img.shape) > 2 and img.shape[2] != 1:
        raise ValueError('The input image should be in grayscale')
    _, seg_img = features.segmentation(img, d, sigma_color, sigma_space,
                                       visualization=True)
    return seg_img


def plot_confusion_matrix(confusion_matrix_file, clim, plot_title=None,
                          plot_filename=None, xlabel=None, ylabel=None):
    if plot_filename is None:
        plot_filename = os.path.join(
            'figures',
            os.path.basename(confusion_matrix_file).split('.')[0] + '.png'
        )
    if plot_title is None:
        plot_title = os.path.basename(confusion_matrix_file).split('.')[0]
    xlabel = 'Ground truth' if xlabel is None else xlabel
    ylabel = 'Predicted' if ylabel is None else ylabel

    print('Plotting confusion matrix from {:s}...'.format(confusion_matrix_file))
    mat = pd.read_csv(confusion_matrix_file, index_col=0)
    mat = mat.to_numpy()

    # Prepare params
    cmap = plt.get_cmap('Blues')
    thresh = np.nanmax(mat) * 0.6

    # Plot the matrix
    plt.figure(figsize=(12, 8))
    plt.imshow(mat, interpolation='nearest', cmap=cmap)
    plt.title(plot_title, fontsize=16)
    plt.colorbar()
    plt.clim(clim)

    # Add class names
    tick_marks = np.arange(10)
    plt.xticks(tick_marks, cols, rotation=45, fontsize=16)
    plt.yticks(tick_marks, cols, rotation=45, fontsize=16)

    for i, j in itertools.product(range(mat.shape[0]), range(mat.shape[1])):
        plt.text(j, i, '{:.2f}'.format(mat[i, j]),
                 horizontalalignment='center',
                 color='white' if mat[i, j] > thresh else 'black',
                 fontsize=16)

    plt.xlabel(xlabel, fontsize=16)
    plt.ylabel(ylabel, fontsize=16)

    # Save plot to file
    plt.tight_layout()
    plt.savefig(plot_filename, dpi=300)
    print('Plot saved to {:s}'.format(plot_filename))


if __name__ == '__main__':

    plot_confusion_matrix(
        'results/results_may03binary_classification_results_f1.csv',
        (0.0, 1.0)
    )
