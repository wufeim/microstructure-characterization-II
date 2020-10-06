#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename: main.py
# @Date: 2020-06-19
# @Author: Wufei Ma

import sys

from PyQt5.QtWidgets import (QApplication, QWidget, QGroupBox, QPushButton, QVBoxLayout, QHBoxLayout, QLabel)
from PyQt5.QtGui import QDesktopServices, QIcon
from PyQt5.QtCore import QUrl, QSize

from featureDialog import FeatureDialog
from segmentationDialog import SegmentationDialog


class MainWindow(QWidget):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.createLeftGroup()
        self.createRightGroup()

        hbox = QHBoxLayout()
        hbox.addWidget(self.leftGroup)
        hbox.addWidget(self.rightGroup)

        self.setLayout(hbox)

        self.setWindowTitle('Microstructure Image Analysis')
        self.resize(480, 320)

    def createLeftGroup(self):
        self.leftGroup = QGroupBox('Start')

        featureBtn = QPushButton('Feature collection')
        featureBtn.setToolTip('Collect features from images and export as csv.')
        featureBtn.clicked.connect(self.openFeatureDialog)

        segmentationBtn = QPushButton('Image segmentation')
        segmentationBtn.setToolTip('Visualize segmentation results.')
        segmentationBtn.clicked.connect(self.openSegmentationDialog)

        visualizationBtn = QPushButton('Visualization')
        visualizationBtn.setToolTip('Visualize collected features.')
        visualizationBtn.setEnabled(False)

        analysisBtn = QPushButton('Feature analysis')
        analysisBtn.setToolTip('Analyze collected features.')
        analysisBtn.setEnabled(False)

        vbox = QVBoxLayout()
        vbox.addWidget(featureBtn)
        vbox.addWidget(segmentationBtn)
        vbox.addWidget(visualizationBtn)
        vbox.addWidget(analysisBtn)
        vbox.addStretch(1)

        self.leftGroup.setLayout(vbox)

    def createRightGroup(self):
        self.rightGroup = QGroupBox('About')

        aboutBtn = QPushButton('About')
        aboutBtn.setToolTip('Open about page in default browser.')
        aboutBtn.clicked.connect(self.openAboutPage)

        docBtn = QPushButton('Documentation')
        docBtn.setToolTip('Open documentation page in default browser.')
        docBtn.clicked.connect(self.openDocPage)

        quitBtn = QPushButton('&Quit')
        quitBtn.clicked.connect(self.close)

        versionLabel = QLabel('v 0.1.0')

        vbox = QVBoxLayout()
        vbox.addWidget(aboutBtn)
        vbox.addWidget(docBtn)
        vbox.addWidget(quitBtn)
        vbox.addWidget(versionLabel)
        vbox.addStretch(1)

        self.rightGroup.setLayout(vbox)

    def openFeatureDialog(self):
        self.hide()
        self.fd = FeatureDialog()
        self.fd.setModal(True)
        self.fd.exec()
        self.show()

    def openSegmentationDialog(self):
        self.hide()
        self.sd = SegmentationDialog()
        self.sd.setModal(True)
        self.sd.exec()
        self.show()

    def openAboutPage(self):
        QDesktopServices.openUrl(QUrl(
            'https://wufeim.github.io/microstructure-characterization-II/',
            QUrl.TolerantMode
        ))

    def openDocPage(self):
        QDesktopServices.openUrl(QUrl(
            'https://wufeim.github.io/microstructure-characterization-II/documentation.html',
            QUrl.TolerantMode
        ))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    app_icon = QIcon()
    app_icon.addFile('static/images/icon_16.png', QSize(16, 16))
    app_icon.addFile('static/images/icon_32.png', QSize(32, 32))
    app_icon.addFile('static/images/icon_64.png', QSize(64, 64))
    app_icon.addFile('static/images/icon_128.png', QSize(128, 128))
    app_icon.addFile('static/images/icon_256.png', QSize(256, 256))
    app_icon.addFile('static/images/icon_512.png', QSize(512, 512))
    app_icon.addFile('static/iamges/icon_1024.png', QSize(1024, 1024))
    app.setWindowIcon(app_icon)

    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
