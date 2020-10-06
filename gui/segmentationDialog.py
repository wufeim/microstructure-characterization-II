#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename: featureDialog.py
# @Date: 2020-06-19
# @Author: Wufei Ma

import os

from PyQt5.QtWidgets import (QDialog, QGridLayout, QGroupBox, QLabel, QLineEdit, QFileDialog, QPushButton, QVBoxLayout,
                             QMessageBox, QMainWindow)
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtCore import QSize, QUrl

from segmentationThread import SegmentationThread


class SegmentationDialog(QDialog, QMainWindow):

    def __init__(self, parent=None):
        super(SegmentationDialog, self).__init__(parent)

        self.createConfigGroup()
        self.createCommandGroup()

        grid = QGridLayout()

        grid.addWidget(self.configGroup, 0, 0)
        grid.addWidget(self.commandGroup, 1, 0)

        grid.setRowStretch(0, 10)
        grid.setRowStretch(1, 10)

        self.setLayout(grid)

        self.setWindowTitle('Image Segmentation')
        self.resize(480, 320)

        self.imageFilename = None
        self.outputPath = None

    def createConfigGroup(self):
        self.configGroup = QGroupBox('Configuration')

        grid = QGridLayout()

        self.imageFilenameEdit = QLineEdit()
        self.loadImageFilenameBtn = QPushButton('')
        self.loadImageFilenameBtn.setIcon(QIcon('static/images/folder.png'))
        self.loadImageFilenameBtn.setIconSize(QSize(12, 12))
        self.loadImageFilenameBtn.setAutoDefault(False)
        self.loadImageFilenameBtn.clicked.connect(self.loadImageFilenameDialog)
        grid.addWidget(QLabel('Image filename'), 0, 0)
        grid.addWidget(self.imageFilenameEdit, 0, 1)
        grid.addWidget(self.loadImageFilenameBtn, 0, 2)

        self.outputPathEdit = QLineEdit()
        self.loadOutputPathBtn = QPushButton('')
        self.loadOutputPathBtn.setIcon(QIcon('static/images/folder.png'))
        self.loadOutputPathBtn.setIconSize(QSize(12, 12))
        self.loadOutputPathBtn.setAutoDefault(False)
        self.loadOutputPathBtn.clicked.connect(self.loadOutputPathDialog)
        grid.addWidget(QLabel('Output path'), 1, 0)
        grid.addWidget(self.outputPathEdit, 1, 1)
        grid.addWidget(self.loadOutputPathBtn, 1, 2)

        grid.setColumnStretch(0, 10)
        grid.setColumnStretch(1, 20)
        grid.setColumnStretch(2, 2)

        self.configGroup.setLayout(grid)

    def createCommandGroup(self):
        self.commandGroup = QGroupBox('Commands')

        vbox = QVBoxLayout()

        self.startBtn = QPushButton('Start')
        self.startBtn.setToolTip('Start image segmentation.')
        self.startBtn.clicked.connect(self.start)
        vbox.addWidget(self.startBtn)

        self.stopBtn = QPushButton('Stop')
        self.stopBtn.setToolTip('Stop image segmentation.')
        self.stopBtn.clicked.connect(self.stop)
        self.stopBtn.setEnabled(False)
        vbox.addWidget(self.stopBtn)

        self.docBtn = QPushButton('Documentation')
        self.docBtn.setToolTip('Open documentation page in default browser.')
        self.docBtn.clicked.connect(self.openDocPage)
        vbox.addWidget(self.docBtn)

        self.closeBtn = QPushButton('Close')
        self.closeBtn.setToolTip('Close the window.')
        self.closeBtn.clicked.connect(self.close)
        vbox.addWidget(self.closeBtn)

        vbox.addStretch(1)

        self.commandGroup.setLayout(vbox)

    def loadImageFilenameDialog(self):
        self.imageFilename, _ = QFileDialog.getOpenFileName(
            self,
            'Load image filename',
            './'
        )
        self.imageFilenameEdit.setText(self.imageFilename)

    def loadOutputPathDialog(self):
        self.outputPath = QFileDialog.getExistingDirectory(
            self,
            'Load output path',
            './'
        )
        self.outputPathEdit.setText(self.outputPath)

    def start(self):
        self.running_mode_ui()

        self.imageFilename = self.imageFilenameEdit.text()
        self.outputPath = self.outputPathEdit.text()

        if not os.path.isfile(self.imageFilename):
            self.critical_msg('The image filename is invalid.')
            self.waiting_mode_ui()
            return None
        if not os.path.isdir(self.outputPath):
            self.critical_msg('The output path is invalid.')
            self.waiting_mode_ui()
            return None

        self.segmentationThread = SegmentationThread(self.imageFilename,
                                                     self.outputPath)
        self.segmentationThread.succeed_signal.connect(self.segmentation_succeed)
        self.segmentationThread.fail_signal.connect(self.segmentation_fail)
        self.segmentationThread.start()

    def stop(self):
        self.segmentationThread.stop()
        self.segmentationThread.quit()
        self.waiting_mode_ui()

    def openDocPage(self):
        QDesktopServices.openUrl(QUrl(
            'https://wufeim.github.io/microstructure-characterization-II/documentation.html',
            QUrl.TolerantMode
        ))

    def critical_msg(self, s):
        QMessageBox.critical(self, 'Error!', s, QMessageBox.Ok)

    def running_mode_ui(self):
        self.startBtn.setEnabled(False)
        self.stopBtn.setEnabled(True)
        self.startBtn.update()
        self.stopBtn.update()

    def waiting_mode_ui(self):
        self.stopBtn.setEnabled(False)
        self.startBtn.setEnabled(True)
        self.stopBtn.update()
        self.startBtn.update()

    def segmentation_succeed(self):
        QMessageBox.information(self, 'Completed!', 'Segmentation outputs saved to {:s}.'.format(self.outputPath),
                                QMessageBox.Ok)
        self.waiting_mode_ui()

    def segmentation_fail(self, s):
        QMessageBox.critical(self, 'Error!', s, QMessageBox.Ok)
