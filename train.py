#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename : train.py
# @Date : 2020-05-03
# @Author : Wufei Ma

import os
import sys
from joblib import dump, load
import collections

import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from models import *
from utils import *

classes = ['DUM1178', 'DUM1154', 'DUM1297', 'DUM1144', 'DUM1150',
           'DUM1160', 'DUM1180', 'DUM1303', 'DUM1142', 'DUM1148']
column1 = ['DUM1178', 'DUM1154', 'DUM1297', 'DUM1144', 'DUM1150', 'DUM1160']
column2 = ['DUM1180', 'DUM1303', 'DUM1142', 'DUM1148']

features_file = 'features_feb02.csv'


def train(mode, feature_names, output_dir, model_dir, output_prefix, logger):
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    if not os.path.isdir(model_dir):
        os.mkdir(model_dir)

    logger.log('\n' + '-' * 32)
    logger.log('Training mode:')
    logger.log('\tmode: {:s}'.format(mode))
    logger.log('\tOutput saved to: {:s}'.format(output_dir))
    logger.log('\tTrained model saved to: {:s}'.format(model_dir))
    logger.log('\tOutput prefix: {:s}'.format(output_prefix))
    logger.log('\tFeatures used: {:s}'.format(str(feature_names)))

    df = pd.read_csv(features_file, index_col=0)
    X = df[feature_names].to_numpy()
    if mode == '10-class':
        Y = np.array([classes.index(x) for x in df['met_id'].to_numpy()])
    elif mode == 'binary':
        Y = np.array([
            0 if x in column1 else 1
            for x in df['met_id'].to_numpy()
        ])
    else:
        raise ValueError('Unsupported training mode: {:s}'.format(mode))
    model = train_random_forest(X, Y, logger)  # the 5th model
    model_name = os.path.join(model_dir, output_prefix+'_trained_rf_model_for_{:s}.joblib'.format(mode))
    dump(model, model_name)

    logger.log('-' * 32 + '\n')


def binary_classification(df, met_ids):
    df = df.loc[df['met_id'].isin(met_ids)]
    f = df[['area_0', 'area_1', 'area_2']].to_numpy()
    l = df['met_id'].to_numpy()
    l = l == met_ids[1]
    if np.sum(l == 0) == 0 or np.sum(l == 1) == 0:
        return np.nan, np.nan
    return train_random_forest_f1_mcc(f[:, :2], l)


def train_binary_classification(output_dir, output_prefix, logger):
    logger.log('\n' + '-' * 32)
    logger.log('Running Experiment 4...')
    logger.log('\tOutput saved to: {:s}'.format(output_dir))
    logger.log('\tOutput prefix: {:s}'.format(output_prefix))

    df = pd.read_csv(features_file, index_col=0)

    f1_scores = np.zeros((len(classes), len(classes)))
    mcc_scores = np.zeros((len(classes), len(classes)))
    for i in range(len(classes)):
        for j in range(len(classes)):
            if i > j:
                continue
            elif i == j:
                f1_scores[i, j] = np.nan
                mcc_scores[i, j] = np.nan
                f1_scores[j, i] = np.nan
                mcc_scores[j, i] = np.nan
            else:
                f1_scores[i, j], mcc_scores[i, j] = binary_classification(df, [classes[i], classes[j]])
                f1_scores[j, i], mcc_scores[j, i] = f1_scores[i, j], mcc_scores[i, j]
                print('For class {:s} and {:s}: F1 score: {:.3f}; MCC score: {:.3f}.'
                      .format(classes[i], classes[j], f1_scores[i, j], mcc_scores[i, j]))

    f1_results = pd.DataFrame(f1_scores)
    mcc_results = pd.DataFrame(mcc_scores)
    f1_results.columns = classes
    mcc_results.columns = classes
    f1_results.insert(0, 'class', classes)
    mcc_results.insert(0, 'class', classes)
    f1_results.set_index('class', inplace=True)
    mcc_results.set_index('class', inplace=True)

    f1_results.to_csv(os.path.join(output_dir, output_prefix+'binary_classification_results_f1.csv'))
    mcc_results.to_csv(os.path.join(output_dir, output_prefix+'binary_classification_results_mcc.csv'))

    logger.log('-' * 32 + '\n')


if __name__ == '__main__':

    ##################
    ## Model Config ##
    ##################

    # Step 1/3:
    # Comment/uncomment the following lines to choose the feature set for
    # Task a and Task b
    feature_names = []
    feature_names += ['area_{:d}'.format(i) for i in range(3)]
    feature_names += ['spatial_{:d}'.format(i) for i in range(14)]
    feature_names += ['haralick_{:d}'.format(i) for i in range(13)]
    feature_names += ['lbp_{:d}'.format(i) for i in range(12)]

    # Step 2/3:
    # Set output directory and file prefix
    output_dir = 'results'
    model_dir = 'train_models'
    output_prefix = 'results_may03'

    # Step 3/3:
    # Comment/uncomment the following lines to choose experiments
    # Task a:        10-class classification to predict microstructure
    #                processing history
    # Task b:        Binary classification to predict the homogenization
    #                temperatures
    # Experiment 4:  Binary classification between two processing histories
    #                based on area features
    experiment_list = []
    experiment_list.append('Task-a')
    experiment_list.append('Task-b')
    experiment_list.append('Experiment-4')

    ####################
    ## Start training ##
    ####################

    # Define logger
    logger = Logger(os.path.join(output_dir, output_prefix+'_log.txt'))

    # Task a
    if 'Task-a' in experiment_list:
        train(mode='10-class',
              feature_names=feature_names,
              output_dir=output_dir,
              model_dir=model_dir,
              output_prefix=output_prefix,
              logger=logger)

    # Task b
    if 'Task-b' in experiment_list:
        train(mode='binary',
              feature_names=feature_names,
              output_dir=output_dir,
              model_dir=model_dir,
              output_prefix=output_prefix,
              logger=logger)

    # Experiment 4
    if 'Experiment-4' in experiment_list:
        train_binary_classification(output_dir=output_dir,
                                    output_prefix=output_prefix,
                                    logger=logger)

    # Save to log file
    logger.flush()
