#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename: paramDialog.py
# @Date: 2020-06-19
# @Author: Wufei Ma

from PyQt5.QtWidgets import (QDialog, QGridLayout, QGroupBox, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox,
                             QMainWindow)
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl, pyqtSignal


class ParamDialog(QDialog, QMainWindow):

    returnParamSignal = pyqtSignal(dict)

    def __init__(self, params, parent=None):
        super(ParamDialog, self).__init__(parent)

        self.distance = params['distance']
        self.P = params['P']
        self.R = params['R']
        self.d = params['d']
        self.sigma_color = params['sigma_color']
        self.sigma_space = params['sigma_space']
        self.kernel_size0 = params['ksize0']
        self.kernel_size1 = params['ksize1']
        self.kernel_size2 = params['ksize2']
        self.kernel_size3 = params['ksize3']

        self.createParamGroup()
        self.createKernelGroup1()
        self.createKernelGroup2()
        self.createCommandGroup()

        grid = QGridLayout()

        grid.addWidget(self.paramGroup, 0, 0)
        grid.addWidget(self.kernel_group1, 1, 0)
        grid.addWidget(self.kernel_group2, 2, 0)
        grid.addWidget(self.commandGroup, 3, 0)

        grid.setRowStretch(0, 10)
        grid.setRowStretch(1, 10)

        self.setLayout(grid)

        self.setWindowTitle('Parameter Settings')
        self.resize(480, 320)

    def createParamGroup(self):
        self.paramGroup = QGroupBox('Parameters')

        grid = QGridLayout()

        self.distanceEdit = QLineEdit()
        self.distanceEdit.setPlaceholderText(str(self.distance))
        grid.addWidget(QLabel('distance ='), 0, 0)
        grid.addWidget(self.distanceEdit, 0, 1)

        self.PEdit = QLineEdit()
        self.PEdit.setPlaceholderText(str(self.P))
        grid.addWidget(QLabel('P ='), 0, 2)
        grid.addWidget(self.PEdit, 0, 3)

        self.REdit = QLineEdit()
        self.REdit.setPlaceholderText(str(self.R))
        grid.addWidget(QLabel('R ='), 1, 0)
        grid.addWidget(self.REdit, 1, 1)

        self.dEdit = QLineEdit()
        self.dEdit.setPlaceholderText(str(self.d))
        grid.addWidget(QLabel('d ='), 1, 2)
        grid.addWidget(self.dEdit, 1, 3)

        self.sigmaColorEdit = QLineEdit()
        self.sigmaColorEdit.setPlaceholderText(str(self.sigma_color))
        grid.addWidget(QLabel('sigma_color ='), 2, 0)
        grid.addWidget(self.sigmaColorEdit, 2, 1)

        self.sigmaSpaceEdit = QLineEdit()
        self.sigmaSpaceEdit.setPlaceholderText(str(self.sigma_space))
        grid.addWidget(QLabel('sigma_space ='), 2, 2)
        grid.addWidget(self.sigmaSpaceEdit, 2, 3)

        grid.setColumnStretch(0, 10)
        grid.setColumnStretch(1, 10)
        grid.setColumnStretch(2, 10)
        grid.setColumnStretch(3, 10)

        self.paramGroup.setLayout(grid)

    def createKernelGroup1(self):
        self.kernel_group1 = QGroupBox('Closing then opening kernel size (k x k)')

        grid = QGridLayout()

        self.kernel_size0_edit = QLineEdit()
        self.kernel_size0_edit.setPlaceholderText(str(self.kernel_size0))
        grid.addWidget(QLabel('Closing k ='), 0, 0)
        grid.addWidget(self.kernel_size0_edit, 0, 1)

        self.kernel_size1_edit = QLineEdit()
        self.kernel_size1_edit.setPlaceholderText(str(self.kernel_size1))
        grid.addWidget(QLabel('Opening k ='), 0, 2)
        grid.addWidget(self.kernel_size1_edit, 0, 3)

        grid.setColumnStretch(0, 10)
        grid.setColumnStretch(1, 10)
        grid.setColumnStretch(2, 10)
        grid.setColumnStretch(3, 10)

        self.kernel_group1.setLayout(grid)

    def createKernelGroup2(self):
        self.kernel_group2 = QGroupBox('Opening then closing kernel size (k x k)')

        grid = QGridLayout()

        self.kernel_size2_edit = QLineEdit()
        self.kernel_size2_edit.setPlaceholderText(str(self.kernel_size2))
        grid.addWidget(QLabel('Opening k ='), 0, 0)
        grid.addWidget(self.kernel_size2_edit, 0, 1)

        self.kernel_size3_edit = QLineEdit()
        self.kernel_size3_edit.setPlaceholderText(str(self.kernel_size3))
        grid.addWidget(QLabel('Closing k ='), 0, 2)
        grid.addWidget(self.kernel_size3_edit, 0, 3)

        grid.setColumnStretch(0, 10)
        grid.setColumnStretch(1, 10)
        grid.setColumnStretch(2, 10)
        grid.setColumnStretch(3, 10)

        self.kernel_group2.setLayout(grid)

    def createCommandGroup(self):
        self.commandGroup = QGroupBox('Commands')

        vbox = QVBoxLayout()

        self.submitBtn = QPushButton('Submit')
        self.submitBtn.setToolTip('Save the parameters.')
        self.submitBtn.clicked.connect(self.submit)
        vbox.addWidget(self.submitBtn)

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

    def submit(self):
        submit_params = {}

        if self.distanceEdit.text() == '':
            submit_params['distance'] = 1
        else:
            try:
                submit_params['distance'] = int(self.distanceEdit.text())
            except:
                QMessageBox.critical(self, 'Error!', 'Invalid input for distance.', QMessageBox.Ok)
                return None

        if self.PEdit.text() == '':
            submit_params['P'] = 10
        else:
            try:
                submit_params['P'] = int(self.PEdit.text())
            except:
                QMessageBox.critical(self, 'Error!', 'Invalid input for P.', QMessageBox.Ok)
                return None

        if self.REdit.text() == '':
            submit_params['R'] = 5
        else:
            try:
                submit_params['R'] = int(self.REdit.text())
            except:
                QMessageBox.critical(self, 'Error!', 'Invalid input for R.', QMessageBox.Ok)
                return None

        if self.dEdit.text() == '':
            submit_params['d'] = 15
        else:
            try:
                submit_params['d'] = int(self.dEdit.text())
            except:
                QMessageBox.critical(self, 'Error!', 'Invalid input for d.', QMessageBox.Ok)
                return None

        if self.sigmaColorEdit.text() == '':
            submit_params['sigma_color'] = 75
        else:
            try:
                submit_params['sigma_color'] = int(self.sigmaColorEdit.text())
            except:
                QMessageBox.critical(self, 'Error!', 'Invalid input for sigma_color.', QMessageBox.Ok)
                return None

        if self.sigmaSpaceEdit.text() == '':
            submit_params['sigma_space'] = 75
        else:
            try:
                submit_params['sigma_space'] = int(self.sigmaSpaceEdit.text())
            except:
                QMessageBox.critical(self, 'Error!', 'Invalid input for sigma_space.', QMessageBox.Ok)
                return None

        if self.kernel_size0_edit.text() == '':
            submit_params['ksize0'] = 9
        else:
            try:
                submit_params['ksize0'] = int(self.kernel_size0_edit.text())
            except:
                QMessageBox.critical(self, 'Error!', 'Invalid input for ksize0.', QMessageBox.Ok)
                return None

        if self.kernel_size1_edit.text() == '':
            submit_params['ksize1'] = 9
        else:
            try:
                submit_params['ksize1'] = int(self.kernel_size1_edit.text())
            except:
                QMessageBox.critical(self, 'Error!', 'Invalid input for ksize1.', QMessageBox.Ok)
                return None

        if self.kernel_size2_edit.text() == '':
            submit_params['ksize2'] = 9
        else:
            try:
                submit_params['ksize2'] = int(self.kernel_size2_edit.text())
            except:
                QMessageBox.critical(self, 'Error!', 'Invalid input for ksize2.', QMessageBox.Ok)
                return None

        if self.kernel_size3_edit.text() == '':
            submit_params['ksize3'] = 3
        else:
            try:
                submit_params['ksize3'] = int(self.kernel_size3_edit.text())
            except:
                QMessageBox.critical(self, 'Error!', 'Invalid input for ksize3.', QMessageBox.Ok)
                return None

        self.returnParamSignal.emit(submit_params)

        self.close()

    def openDocPage(self):
        QDesktopServices.openUrl(QUrl(
            'http://wufeim.github.io/microstructure-characterization-II/documentation.html',
            QUrl.TolerantMode
        ))


if __name__ == '__main__':
    pass
