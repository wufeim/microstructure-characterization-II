import numpy as np
import pandas as pd

import cv2

from features.features import *

FEATURE_NAMES = [
    'area',
    'spatial',
    'haralick',
    'lbp'
]


def collect_features_by_filenames(filenames, feature_names, **kwargs):
    for fn in feature_names:
        if fn not in FEATURE_NAMES:
            raise Exception('Unknown feature name: {:s}'.format(fn))
    feature = []

    d = kwargs['d'] if 'd' in kwargs else 15
    sigma_color = kwargs['sigma_color'] if 'area_sigma_color' in kwargs else 75
    sigma_space = kwargs['sigma_space'] if 'area_sigma_space' in kwargs else 75
    with_info_bar = kwargs['with_info_bar'] if 'with_info_bar' in kwargs else True
    distance = kwargs['distance'] if 'distance' in kwargs else 1
    P = kwargs['P'] if 'P' in kwargs else 10
    R = kwargs['R'] if 'R' in kwargs else 5

    if 'area' in feature_names:
        f = area_features(image_names=filenames,
                          d=d,
                          sigma_color=sigma_color,
                          sigma_space=sigma_space,
                          with_info_bar=with_info_bar)
        if len(feature) == 0:
            feature = f
        else:
            feature = np.hstack((feature, f))

    if 'spatial' in feature_names:
        f = spatial_features(image_names=filenames,
                             d=d,
                             sigma_color=sigma_color,
                             sigma_space=sigma_space,
                             with_info_bar=with_info_bar)
        if len(feature) == 0:
            feature = f
        else:
            feature = np.hstack((feature, f))

    if 'haralick' in feature_names:
        f = haralick_features(image_names=filenames,
                              distance=distance)
        if len(feature) == 0:
            feature = f
        else:
            feature = np.vstack((feature, f))

    if 'lbp' in feature_names:
        f = lbp_features(image_names=filenames,
                         P=P,
                         R=R)
        if len(feature) == 0:
            feature = f
        else:
            feature = np.vstack((feature, f))

    return feature


if __name__ == '__main__':

    pass
