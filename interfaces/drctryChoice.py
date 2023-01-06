# Form implementation generated from reading ui file 'drctryChoice.ui'
#
# Created by: PyQt6 UI code generator 6.1.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QFileDialog


class Ui_drctryChoice(object):
    def setupUi(self, drctryChoice):
        drctryChoice.setObjectName("drctryChoice")
        drctryChoice.resize(706, 95)
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        drctryChoice.setFont(font)
        drctryChoice.setStyleSheet("background-color: rgb(61, 255, 200);\n"
                                   "border-color: rgb(7, 7, 7);")
        self.lineEdit = QtWidgets.QLineEdit(drctryChoice)
        self.lineEdit.setGeometry(QtCore.QRect(200, 27, 381, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit.setFont(font)
        self.lineEdit.setStyleSheet("background-color: rgb(255, 255, 255);\n"
                                    "color: rgb(0, 0, 0);")
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.pushButton = QtWidgets.QPushButton(drctryChoice)
        self.pushButton.setGeometry(QtCore.QRect(600, 33, 93, 29))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton.setFont(font)
        self.pushButton.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.pushButton.setObjectName("pushButton")
        self.label = QtWidgets.QLabel(drctryChoice)
        self.label.setGeometry(QtCore.QRect(10, 37, 161, 21))
        font = QtGui.QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")

        self.retranslateUi(drctryChoice)
        QtCore.QMetaObject.connectSlotsByName(drctryChoice)

    def retranslateUi(self, drctryChoice):
        _translate = QtCore.QCoreApplication.translate
        drctryChoice.setWindowTitle(_translate("drctryChoice", "Выберите папку для сохранения справки"))
        self.lineEdit.setPlaceholderText(_translate("drctryChoice", "Введите папку для сохранения паспорта"))
        self.pushButton.setText(_translate("drctryChoice", "Обзор"))
        self.label.setText(_translate("drctryChoice", "Папка для отчета"))

    def get_report_directory(self):
        dirlist = QFileDialog.getExistingDirectory()
        self.lineEdit.setText(dirlist)
        with open('path_neutron_report.txt', 'w') as f:
            f.write(dirlist)
        print(f'{dirlist=}')
