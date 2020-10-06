#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename: featureDialog.py
# @Date: 2020-06-19
# @Author: Wufei Ma

import os
import fnmatch
from datetime import date, datetime

from PyQt5.QtWidgets import (QDialog, QGridLayout, QGroupBox, QLabel,
    QLineEdit, QFileDialog, QPushButton, QSizePolicy, QVBoxLayout,
    QCheckBox, QTextEdit, QProgressBar, QMessageBox, QMainWindow)
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtCore import QSize, QUrl

from featureCollectionThread import FeatureCollectionThread
from paramDialog import ParamDialog


class FeatureDialog(QDialog, QMainWindow):

    def __init__(self, parent=None):
        super(FeatureDialog, self).__init__(parent)

        self.createConfigGroup()
        self.createFeatureGroup()
        self.createOutputGroup()
        self.createCommandGroup()

        grid = QGridLayout()

        grid.addWidget(self.configGroup, 0, 0)
        grid.addWidget(self.featureGroup, 0, 1)
        grid.addWidget(self.outputGroup, 1, 0)
        grid.addWidget(self.commandGroup, 1, 1)

        grid.setColumnStretch(0, 20)
        grid.setColumnStretch(1, 10)
        grid.setRowStretch(0, 10)
        grid.setRowStretch(1, 10)

        self.setLayout(grid)

        self.output('Ready.')

        self.setWindowTitle('Feature Collection')
        self.resize(720, 480)

        self.outputPrefix = None
        self.filenamePattern = None
        self.filenamePatternS = None
        self.imagePath = None
        self.outputPath = None
        self.featuresActive = [False] * 4

        self.fc = None

        self.params = {}
        self.params['distance'] = 1
        self.params['P'] = 10
        self.params['R'] = 5
        self.params['d'] = 15
        self.params['sigma_color'] = 75
        self.params['sigma_space'] = 75
        self.params['ksize0'] = 9
        self.params['ksize1'] = 9
        self.params['ksize2'] = 9
        self.params['ksize3'] = 3

    def createConfigGroup(self):
        self.configGroup = QGroupBox('Configuration')

        grid = QGridLayout()

        self.outputPrefixEdit = QLineEdit()
        self.outputPrefixEdit.setPlaceholderText('feature-collection-'+str(date.today()))
        grid.addWidget(QLabel('Output prefix:'), 0, 0)
        grid.addWidget(self.outputPrefixEdit, 0, 1, 1, 2)
        self.outputPrefixEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.filenamePatternEdit = QLineEdit()
        grid.addWidget(QLabel('Image filename pattern:'), 1, 0)
        self.filenamePatternEdit.setPlaceholderText('*.tiff *.png')
        grid.addWidget(self.filenamePatternEdit, 1, 1, 1, 2)
        self.filenamePatternEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.imagePathEdit = QLineEdit()
        self.loadImagePathBtn = QPushButton('')
        self.loadImagePathBtn.setIcon(QIcon('static/images/folder.png'))
        self.loadImagePathBtn.setIconSize(QSize(12, 12))
        self.loadImagePathBtn.setAutoDefault(False)
        self.loadImagePathBtn.clicked.connect(self.loadImagePathDialog)
        grid.addWidget(QLabel('Image path'), 2, 0)
        grid.addWidget(self.imagePathEdit, 2, 1)
        grid.addWidget(self.loadImagePathBtn, 2, 2)

        self.outputPathEdit = QLineEdit()
        self.loadOutputPathBtn = QPushButton('')
        self.loadOutputPathBtn.setIcon(QIcon('static/images/folder.png'))
        self.loadOutputPathBtn.setIconSize(QSize(12, 12))
        self.loadOutputPathBtn.setAutoDefault(False)
        self.loadOutputPathBtn.clicked.connect(self.loadOutputPathDialog)
        grid.addWidget(QLabel('Output path'), 3, 0)
        grid.addWidget(self.outputPathEdit, 3, 1)
        grid.addWidget(self.loadOutputPathBtn, 3, 2)

        grid.setColumnStretch(0, 10)
        grid.setColumnStretch(1, 20)
        grid.setColumnStretch(2, 2)

        self.configGroup.setLayout(grid)

    def createFeatureGroup(self):
        self.featureGroup = QGroupBox('Features')

        vbox = QVBoxLayout()

        self.featureCheckBoxes = []
        self.featureCheckBoxes.append(QCheckBox('Area features'))
        self.featureCheckBoxes.append(QCheckBox('Spatial features'))
        self.featureCheckBoxes.append(QCheckBox('Haralick features'))
        self.featureCheckBoxes.append(QCheckBox('LBP features'))

        for i in range(4):
            vbox.addWidget(self.featureCheckBoxes[i])

        vbox.addStretch(1)

        self.featureGroup.setLayout(vbox)

    def createOutputGroup(self):
        self.outputGroup = QGroupBox('Outputs')

        vbox = QVBoxLayout()

        self.statusLabel = QLabel('Status: Ready')
        vbox.addWidget(self.statusLabel)

        self.outputArea = QTextEdit()
        vbox.addWidget(self.outputArea)

        self.progressBar = QProgressBar()
        self.progressBar.setFormat('%v%')
        self.progressBar.setValue(100)
        vbox.addWidget(self.progressBar)

        vbox.addStretch(1)

        self.outputGroup.setLayout(vbox)

    def createCommandGroup(self):
        self.commandGroup = QGroupBox('Commands')

        vbox = QVBoxLayout()

        self.startBtn = QPushButton('Start')
        self.startBtn.setToolTip('Start feature collection.')
        self.startBtn.clicked.connect(self.start)
        vbox.addWidget(self.startBtn)

        self.stopBtn = QPushButton('Stop')
        self.stopBtn.setToolTip('Stop feature collection. Collected features would not be saved.')
        self.stopBtn.clicked.connect(self.stop)
        self.stopBtn.setEnabled(False)
        vbox.addWidget(self.stopBtn)

        self.paramBtn = QPushButton('Parameters')
        self.paramBtn.setToolTip('Edit parameter settings.')
        self.paramBtn.clicked.connect(self.openParamDialog)
        vbox.addWidget(self.paramBtn)

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

    def openParamDialog(self):
        self.pd = ParamDialog(self.params)
        self.pd.returnParamSignal.connect(self.setParam)
        self.pd.setModal(True)
        self.pd.exec()

    def loadImagePathDialog(self):
        self.imagePath = QFileDialog.getExistingDirectory(
            self,
            'Load image path',
            './'
        )
        self.imagePathEdit.setText(self.imagePath)

    def loadOutputPathDialog(self):
        self.outputPath = QFileDialog.getExistingDirectory(
            self,
            'Load output path',
            './'
        )
        self.outputPathEdit.setText(self.outputPath)

    def openDocPage(self):
        QDesktopServices.openUrl(QUrl(
            'https://wufeim.github.io/microstructure-characterization-II/documentation.html',
            QUrl.TolerantMode
        ))

    def validate(self):
        if self.imagePath == '':
            return False, 'Error: Please specify the path to the images.'
        if not os.path.isdir(self.imagePath):
            return False, 'Error: The path to the images is not valid.'
        if self.outputPath == '':
            return False, 'Error: Please specify the path to save outputs.'
        if not os.path.isdir(self.outputPath):
            return False, 'Error: The path for output files is not valid.'

        if not (self.featuresActive[0] or self.featuresActive[1] or self.featuresActive[2] or self.featuresActive[3]):
            return False, 'Error: Feature set cannot be empty.'

        return True, None

    def patternMatch(self, s):
        for p in self.filenamePatternS:
            if fnmatch.fnmatch(s, p):
                return True
        return False

    def start(self):
        self.running_mode_ui()

        self.outputPrefix = self.outputPrefixEdit.text()
        self.filenamePattern = self.filenamePatternEdit.text()
        self.imagePath = self.imagePathEdit.text()
        self.outputPath = self.outputPathEdit.text()

        if self.outputPrefix == "":
            self.outputPrefix = "feature-collection-" + str(date.today())
        if self.filenamePattern == "":
            self.filenamePattern = "*.tiff *.png"

        for i in range(4):
            self.featuresActive[i] = self.featureCheckBoxes[i].isChecked()

        ready, msg = self.validate()
        if not ready:
            QMessageBox.critical(self, 'Error!', msg, QMessageBox.Ok)
            self.output(msg)
            self.waiting_mode_ui()
            return None
        self.output('Start collecting features.')

        self.filenamePatternS = self.filenamePattern.split(' ')

        print('self.ouptutPrefix = ', self.outputPrefix)
        print('self.filenamePattern = ', self.filenamePattern)
        print('self.filenamePatternS =', self.filenamePatternS)
        print('self.imagePath =', self.imagePath)
        print('self.outputPath =', self.outputPath)
        print('self.featuresActive =', self.featuresActive)

        filenames = sorted([x for x in os.listdir(self.imagePath)
                            if self.patternMatch(x)])
        filenames = [os.path.join(self.imagePath, x) for x in filenames]

        if len(filenames) == 0:
            QMessageBox.critical(self, 'Error!', 'No images found.', QMessageBox.Ok)
            self.output('No images found.')
            self.waiting_mode_ui()
            return None

        self.progressBarMax = len(filenames) + 2
        self.progressBar.setRange(0, self.progressBarMax)
        self.progressBar.setValue(0)
        self.output('{:d} image files found.'.format(len(filenames)))
        self.incrementProgressBar()

        outputFilename = self.outputPrefix + '_' + str(len(filenames)) + '_'
        for i in range(len(self.featuresActive)):
            outputFilename += '1' if self.featuresActive[i] else '0'
        outputFilename = os.path.join(self.outputPath, outputFilename+'.csv')

        self.collectionThread = FeatureCollectionThread(
            filenames, self.featuresActive[0], self.featuresActive[1], self.featuresActive[2], self.featuresActive[3],
            outputFilename, self.params
        )
        self.collectionThread.incremental_signal.connect(self.incrementProgressBar)
        self.collectionThread.output_signal.connect(self.output)
        self.collectionThread.complete_signal.connect(self.completed)
        self.collectionThread.start()

    def stop(self):
        self.output('Thread stopped.')
        self.collectionThread.stop()
        self.collectionThread.quit()
        self.waiting_mode_ui()

    def output(self, s):
        t = datetime.now()
        timestamp = '[{:02d}:{:02d}:{:02d}] '.format(t.hour, t.minute, t.second)
        self.outputArea.append(timestamp + s)
        self.outputArea.verticalScrollBar().setValue(self.outputArea.verticalScrollBar().maximum())
        print('[PROGRAM LOG]', s)

    def incrementProgressBar(self):
        self.progressBar.setValue(self.progressBar.value() + 1)

    def completed(self):
        QMessageBox.information(self, 'Completed!', 'Feature collection finished!', QMessageBox.Ok)
        self.waiting_mode_ui()

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
        self.progressBar.setValue(self.progressBar.maximum())

    def setParam(self, params):
        self.params['distance'] = params['distance']
        self.params['P'] = params['P']
        self.params['R'] = params['R']
        self.params['d'] = params['d']
        self.params['sigma_color'] = params['sigma_color']
        self.params['sigma_space'] = params['sigma_space']
        self.params['ksize0'] = params['ksize0']
        self.params['ksize1'] = params['ksize1']
        self.params['ksize2'] = params['ksize2']
        self.params['ksize3'] = params['ksize3']

        self.output('Parameters updated.')
