#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename : models.py
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

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, matthews_corrcoef


def train_random_forest(X, Y, logger):
    if len(Y.shape) > 1:
        Y = Y.flatten()
    skf = StratifiedKFold(n_splits=5)
    count = 1
    acc = []
    f1 = []
    for train_index, test_index in skf.split(np.zeros((len(Y), 1)), Y):
        logger.log('k-fold: #{}'.format(count))
        count += 1
        train_labels = Y[train_index]
        test_labels = Y[test_index]
        train = X[train_index]
        test = X[test_index]
        model = RandomForestClassifier(n_estimators=100, criterion='entropy',
                                       max_features='sqrt',
                                       n_jobs=-1, verbose=0)
        model.fit(train, train_labels)
        n_nodes = []
        max_depths = []

        for ind_tree in model.estimators_:
            n_nodes.append(ind_tree.tree_.node_count)
            max_depths.append(ind_tree.tree_.max_depth)

        logger.log(f'    Average number of nodes {int(np.mean(n_nodes))}')
        logger.log(f'    Average maximum depth {int(np.mean(max_depths))}')

        train_rf_predictions = model.predict(train)
        train_rf_probs = model.predict_proba(train)[:, 1]
        rf_predictions = model.predict(test)
        rf_probs = model.predict_proba(test)[:, 1]

        if np.sum(test_labels == 0) == 0 or np.sum(test_labels == 1) == 0:
            # print('Error: Only one label in test_labels.')
            continue

        a = f1_score(test_labels, rf_predictions, average='weighted')
        f1.append(a)
        logger.log('    F1: {}'.format(a))

        a = sum((rf_predictions == test_labels) / len(test))
        acc.append(a)
        logger.log('    Model accuracy: {}'.format(a))
        logger.log('    Feature importances: {}'.format(model.feature_importances_))

    logger.log('\nAverage accuracy: {}'.format(sum(acc) / len(acc)))
    logger.log('Average F1: {}'.format(sum(f1) / len(f1)))
    return model


def train_random_forest_f1_mcc(X, Y):
    if len(Y.shape) > 1:
        Y = Y.flatten()
    skf = StratifiedKFold(n_splits=5)
    count = 1
    f1_scores = []
    mcc = []
    for train_index, test_index in skf.split(np.zeros((len(Y), 1)), Y):
        count += 1
        train_labels = Y[train_index]
        test_labels = Y[test_index]
        train = X[train_index]
        test = X[test_index]
        model = RandomForestClassifier(n_estimators=100,
                                       max_features='sqrt',
                                       n_jobs=-1, verbose=0)
        model.fit(train, train_labels)
        n_nodes = []
        max_depths = []

        for ind_tree in model.estimators_:
            n_nodes.append(ind_tree.tree_.node_count)
            max_depths.append(ind_tree.tree_.max_depth)

        train_rf_predictions = model.predict(train)
        train_rf_probs = model.predict_proba(train)[:, 1]
        rf_predictions = model.predict(test)
        rf_probs = model.predict_proba(test)[:, 1]

        if np.sum(test_labels == 0) == 0 or np.sum(test_labels == 1) == 0:
            print('Error: Only one label in test_labels.')
            continue
        if np.sum(rf_predictions == 0) == 0 or np.sum(rf_predictions == 1) == 1:
            print('Error: Only one label in rf_predictions.')
            continue

        # a = sum((rf_predictions == test_labels) / len(test))
        f1_scores.append(f1_score(test_labels, rf_predictions,
                                  average='weighted'))
        mcc.append(matthews_corrcoef(test_labels, rf_predictions))
    return np.mean(f1_scores), np.mean(mcc)


if __name__ == '__main__':

    pass
