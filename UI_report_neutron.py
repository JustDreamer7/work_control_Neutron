# pip install PyQt6
# pyuic6 messenger.ui -o clientui.py

# В этом py файле описана логика взаимодействия с интерфейсом


import os
import datetime

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import *

from exceptions import DateError

# from First_Proccessing import First_Proccessing
# from Sec_Proccessing import secProccessing

# from errors import *


from interfaces.interface import Ui_MainWindow
from interfaces.takeFiles import Ui_takeFiles
from interfaces.drctryChoice import Ui_drctryChoice


class Passport(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.widget = QtWidgets.QWidget()
        self.setupUi(self)
        self.runPassport.pressed.connect(self.report_on_click)
        self.runPassport_2.pressed.connect(self.return_files_on_click)
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.radioButton)
        self.button_group.addButton(self.radioButton_2)
        self.radioButton.setChecked(True)
        self.openDirectory.pressed.connect(self.open_report_directory)
        self.openFileDirectory.pressed.connect(self.open_file_directory)
        self.dateEdit_2.setDate(QtCore.QDate(int(str(datetime.datetime.today()).split(' ')[0].split('-')[0]),
                                             int(str(datetime.datetime.today()).split(' ')[0].split('-')[1]),
                                             int(str(datetime.datetime.today()).split(' ')[0].split('-')[2])))
        self.dateEdit_2.setDisplayFormat("dd.MM.yyyy")
        self.dateEdit.setDate(QtCore.QDate(int(str(datetime.datetime.today()).split(' ')[0].split('-')[0]), 1, 1))
        self.dateEdit.setDisplayFormat("dd.MM.yyyy")

    def open_file_directory(self):
        ui_file_drctry = Ui_takeFiles()
        ui_file_drctry.setupUi(self.widget)
        # запись в 2 файла -> 2 кластера, чтобы данные о папке сохранялись в отрыве от работы программы
        try:
            with open('path_neutron_files.txt', 'r') as f:
                ui_file_drctry.lineEdit.setText(f.read())
        except FileNotFoundError:
            ui_file_drctry.lineEdit.setText("")
        try:
            with open('path_uragan_files.txt', 'r') as f2:
                ui_file_drctry.lineEdit_2.setText(f2.read())
        except FileNotFoundError:
            ui_file_drctry.lineEdit_2.setText("")
        try:
            with open('path_vaisala_file.txt', 'r') as f3:
                ui_file_drctry.lineEdit_3.setText(f3.read())
        except FileNotFoundError:
            ui_file_drctry.lineEdit_3.setText("")
        try:
            with open('path_mask_file.txt', 'r') as f4:
                ui_file_drctry.lineEdit_4.setText(f4.read())
        except FileNotFoundError:
            ui_file_drctry.lineEdit_4.setText("")
        ui_file_drctry.pushButton.clicked.connect(
            lambda: Ui_takeFiles.getFileDirectory(ui_file_drctry, 'path_neutron_files'))
        ui_file_drctry.pushButton_2.clicked.connect(
            lambda: Ui_takeFiles.getFileDirectory(ui_file_drctry, 'path_uragan_files'))
        ui_file_drctry.pushButton_3.clicked.connect(
            lambda: Ui_takeFiles.getFileDirectory(ui_file_drctry, 'path_vaisala_file'))
        ui_file_drctry.pushButton_4.clicked.connect(
            lambda: Ui_takeFiles.getFileDirectory(ui_file_drctry, 'path_mask_file'))
        self.widget.show()

    def open_report_directory(self):
        # Возможно нужно переопределять self.widget, чтобы не лагало отображение
        ui_report_drctry = Ui_drctryChoice()
        ui_report_drctry.setupUi(self.widget)
        ui_report_drctry.pushButton.clicked.connect(lambda: Ui_drctryChoice.get_report_directory(ui_report_drctry))
        try:
            with open('path_prisma_report.txt', 'r') as f:
                ui_report_drctry.lineEdit.setText(f.read())
        except FileNotFoundError:
            ui_report_drctry.lineEdit.setText("")
        self.widget.show()

    def return_files_on_click(self):
        # описание работы кнопки получения данных для составления маски
        proccessing_pressure = 0
        if self.radioButton.isChecked():
            proccessing_pressure = 993
        elif self.radioButton_2.isChecked():
            proccessing_pressure = 'mean_value'
        start_date = self.dateEdit.date().toPyDate()
        end_date = self.dateEdit_2.date().toPyDate()
        try:
            if start_date > end_date:
                raise DateError(start_date, end_date)
            with open('path_neutron_report.txt', 'r') as f:
                report_path = f.read()
            picture_path = report_path + '/without_mask_Pics'
            file_path = report_path + '/without_mask_N_files'
            with open('path_neutron_files.txt', 'r') as f:
                file_neutron_data = f.read()
            with open('path_uragan_files.txt', 'r') as f:
                file_uragan_pressure = f.read()
            with open('path_vaisala_file.txt', 'r') as f:
                file_vaisala_pressure = f.read()
            if ~os.path.exists(picture_path):
                try:
                    os.mkdir(picture_path)
                except OSError:
                    print(f"Создать директорию {picture_path} не удалось")
                else:
                    print(f"Успешно создана директория {picture_path}")
            if ~os.path.exists(file_path):
                try:
                    os.mkdir(file_path)
                except OSError:
                    print(f"Создать директорию {file_path} не удалось")
                else:
                    print(f"Успешно создана директория {file_path}")
            # First_Proccessing(int(lst[0][0]), int(lst[0][1]), int(lst[0][2]), int(lst[1][0]), int(lst[1][1]),
            #                       int(lst[1][2]), dirlist, piclist, filelist, file_neutron_data, file_uragan_pressure,
            #                       file_vaisala_pressure, proccessing_pressure)
        except PermissionError:
            print("Закройте предыдущую версию файла!")
        except DateError:
            DateError(start_date, end_date).ui_output_error()

    def report_on_click(self):
        # описание работы кнопки получения паспорта
        start_date = self.dateEdit.date().toPyDate()
        end_date = self.dateEdit_2.date().toPyDate()
        try:
            if start_date > end_date:
                raise DateError(start_date, end_date)
            proccessing_pressure = 0
            if self.radioButton.isChecked():
                proccessing_pressure = 993
            elif self.radioButton_2.isChecked():
                proccessing_pressure = 'mean_value'
            with open('path_neutron_report.txt', 'r') as f:
                report_path = f.read()
            picture_path = report_path + '/Pics'
            with open('path_neutron_files.txt', 'r') as f:
                file_neutron_data = f.read()
            with open('path_uragan_files.txt', 'r') as f:
                file_uragan_pressure = f.read()
            with open('path_mask_file.txt', 'r') as f:
                file_mask = f.read()
            if ~os.path.exists(picture_path):
                try:
                    os.mkdir(picture_path)
                except OSError:
                    print(f"Создать директорию {picture_path} не удалось")
                else:
                    print(f"Успешно создана директория {picture_path}")
            # secProccessing(int(lst[0][0]), int(lst[0][1]), int(lst[0][2]), int(lst[1][0]), int(lst[1][1]),
            #               int(lst[1][2]), dirlist, piclist, file_neutron_data, file_uragan_pressure,
            #               proccessing_pressure, file_mask)
        except PermissionError:
            print("Закройте предыдущую версию файла!")
        except DateError:
            DateError(start_date, end_date).ui_output_error()


# запуск основного окна
app = QtWidgets.QApplication([])
window = Passport()
window.show()
app.exec()

# Не удаляй, код должен остаться, если сломается takeFiles.py

#
#     def getFileDirectory(self, filename):
#         dirlist = QFileDialog.getExistingDirectory()
#         if filename == 'path1files':
#             self.lineEdit.setText(dirlist)
#         elif filename == 'path2files':
#             self.lineEdit_2.setText(dirlist)
#         else:
#             self.lineEdit_3.setText(dirlist)
#         with open(filename + '.ini', 'w') as f:
#             f.write(dirlist)
#         print(dirlist)
