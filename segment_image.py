#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename : segment_image.py
# @Date : 2020-05-06
# @Author : Wufei Ma

import os
import sys
import argparse
import cv2
import utils


parser = argparse.ArgumentParser(description='Microstructure image segmentation.')
parser.add_argument('img_file', type=str, metavar='img_file',
                    help='path to the image file')
args = parser.parse_args()

img = cv2.imread(args.img_file, cv2.IMREAD_GRAYSCALE)
if img is None:
    raise ValueError('Failed to read the image: {:s}'.format(args.img_file))
img = utils.segment_image(img)

out_file = os.path.join(
    'figures',
    'segmentation_' + os.path.basename(args.img_file).split('.')[0] + '.png'
)
cv2.imwrite(out_file, img)
