import datetime
import os
import warnings

import numpy as np
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import *

from exceptions import DateError
from file_reader.accessory_files_reader import AccessoryFileReader
# from file_reader.db_file_reader import DbFileReader
from file_reader.mask_file_reader import MaskFileReader
from file_reader.neutron_file_reader import NeutronFileReader
from file_reader.pressure_file_reader import PressureFileReader
from file_reader.vaisala_file_reader import VaisalaFileReader
from interfaces.drctryChoice import Ui_drctryChoice
from interfaces.interface import Ui_MainWindow
from interfaces.takeFiles import Ui_takeFiles
from make_excel_neutron import make_excel_neutron
from make_report_neutron import make_report_neutron

# from errors import *
warnings.filterwarnings(action='ignore')


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
            with open('path_vaisala_files.txt', 'r') as f3:
                ui_file_drctry.lineEdit_3.setText(f3.read())
        except FileNotFoundError:
            ui_file_drctry.lineEdit_3.setText("")
        try:
            with open('path_mask_files.txt', 'r') as f4:
                ui_file_drctry.lineEdit_4.setText(f4.read())
        except FileNotFoundError:
            ui_file_drctry.lineEdit_4.setText("")
        ui_file_drctry.pushButton.clicked.connect(
            lambda: Ui_takeFiles.getFileDirectory(ui_file_drctry, 'path_neutron_files'))
        ui_file_drctry.pushButton_2.clicked.connect(
            lambda: Ui_takeFiles.getFileDirectory(ui_file_drctry, 'path_uragan_files'))
        ui_file_drctry.pushButton_3.clicked.connect(
            lambda: Ui_takeFiles.getFileDirectory(ui_file_drctry, 'path_vaisala_files'))
        ui_file_drctry.pushButton_4.clicked.connect(
            lambda: Ui_takeFiles.getFileDirectory(ui_file_drctry, 'path_mask_files'))
        self.widget.show()

    def open_report_directory(self):
        # Возможно нужно переопределять self.widget, чтобы не лагало отображение
        ui_report_drctry = Ui_drctryChoice()
        ui_report_drctry.setupUi(self.widget)
        ui_report_drctry.pushButton.clicked.connect(lambda: Ui_drctryChoice.get_report_directory(ui_report_drctry))
        try:
            with open('path_neutron_report.txt', 'r') as f:
                ui_report_drctry.lineEdit.setText(f.read())
        except FileNotFoundError:
            ui_report_drctry.lineEdit.setText("")
        self.widget.show()

    def return_files_on_click(self):
        # описание работы кнопки получения данных для составления маски
        start_date = self.dateEdit.date().toPyDate()
        end_date = self.dateEdit_2.date().toPyDate()
        try:
            if start_date > end_date:
                raise DateError(start_date, end_date)
            with open('path_neutron_report.txt', 'r') as f:
                report_path = f.read()
            picture_path = report_path + '/without_mask_Pics'
            files_path = report_path + '/without_mask_N_files'
            with open('path_neutron_files.txt', 'r') as f:
                file_neutron_data = f.read()
            with open('path_uragan_files.txt', 'r') as f:
                file_uragan_pressure = f.read()
            with open('path_vaisala_files.txt', 'r') as f:
                file_vaisala_pressure = f.read()
            if not os.path.exists(picture_path):
                try:
                    os.mkdir(picture_path)
                except OSError:
                    print(f"Создать директорию {picture_path} не удалось")
                else:
                    print(f"Успешно создана директория {picture_path}")
            if not os.path.exists(files_path):
                try:
                    os.mkdir(files_path)
                except OSError:
                    print(f"Создать директорию {files_path} не удалось")
                else:
                    print(f"Успешно создана директория {files_path}")
            neutron_data = NeutronFileReader.preparing_data(start_date=start_date,
                                                            end_date=end_date,
                                                            path_to_files=file_neutron_data)
            pressure_data = PressureFileReader.preparing_data(start_date=start_date,
                                                              end_date=end_date,
                                                              path_to_files=file_uragan_pressure)
            vaisala_data = VaisalaFileReader.preparing_data(start_date=start_date,
                                                            end_date=end_date,
                                                            path_to_files=file_vaisala_pressure)
            pressure_data = NeutronFileReader.cutting_pressure_data_from_neutron_data(neutron_data=neutron_data,
                                                                                      pressure_data=pressure_data)
            neutron_data = PressureFileReader.cutting_neutron_data_from_pressure_data(neutron_data=neutron_data,
                                                                                      pressure_data=pressure_data)

            corr_pressure_data = PressureFileReader.change_pressure_interval(pressure_data=pressure_data,
                                                                             neutron_data=neutron_data)
            # В corr_pressure_data присутствуют NaN их надо убрать
            if np.isnan(corr_pressure_data).any():
                print("Есть NaN или inf в corr_pressure")

            if len(corr_pressure_data) > len(neutron_data.index):
                print(f'{len(corr_pressure_data)=}')
                print(f'{len(neutron_data.index)=}')
                print('Заглушка для бага, где после корректировки данных по давлению. Они все равно плохи.')
                corr_pressure_data = corr_pressure_data[:len(neutron_data.index)]

            proccessing_pressure = self.proccessing_pressure_choice(corr_pressure_data)

            make_excel_neutron(start_date=start_date, end_date=end_date, files_path=files_path,
                               picture_path=picture_path, neutron_data=neutron_data, pressure_data=corr_pressure_data,
                               vaisala_data=vaisala_data, proccessing_pressure=proccessing_pressure)

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
            with open('path_neutron_report.txt', 'r') as f:
                report_path = f.read()
            picture_path = report_path + '/Pics'
            with open('path_neutron_files.txt', 'r') as f:
                file_neutron_data = f.read()
            with open('path_uragan_files.txt', 'r') as f:
                file_uragan_pressure = f.read()
            with open('path_mask_files.txt', 'r') as f:
                file_mask = f.read()
            if not os.path.exists(picture_path):
                try:
                    os.mkdir(picture_path)
                except OSError:
                    print(f"Создать директорию {picture_path} не удалось")
                else:
                    print(f"Успешно создана директория {picture_path}")
            neutron_data = NeutronFileReader.preparing_data(start_date=start_date,
                                                            end_date=end_date,
                                                            path_to_files=file_neutron_data)
            accessory_data = AccessoryFileReader(start_date=start_date, end_date=end_date,
                                                 path_to_files=file_neutron_data)
            pressure_data = PressureFileReader.preparing_data(start_date=start_date,
                                                              end_date=end_date,
                                                              path_to_files=file_uragan_pressure)

            pressure_data = NeutronFileReader.cutting_pressure_data_from_neutron_data(neutron_data=neutron_data,
                                                                                      pressure_data=pressure_data)
            neutron_data = PressureFileReader.cutting_neutron_data_from_pressure_data(neutron_data=neutron_data,
                                                                                      pressure_data=pressure_data)

            for mask_det in range(1, 5):
                try:
                    mask_reader = MaskFileReader(path_to_files=file_mask, detector=mask_det)
                    mask_period_data, mask_without_periods = mask_reader.reading_file()
                    neutron_data = MaskFileReader.correct_neutron_data(neutron_data=neutron_data,
                                                                       mask_without_periods=mask_without_periods,
                                                                       period_mask=mask_period_data,
                                                                       detector=mask_det)
                except FileNotFoundError:
                    print(f"Mask data from {mask_det} detector doesn't exist")

            corr_pressure_data = PressureFileReader.change_pressure_interval(pressure_data=pressure_data,
                                                                             neutron_data=neutron_data)
            # В corr_pressure_data присутствуют NaN их надо убрать
            if np.isnan(corr_pressure_data).any():
                print("Есть NaN или inf в corr_pressure")

            if len(corr_pressure_data) > len(neutron_data.index):
                print(f'{len(corr_pressure_data)=}')
                print(f'{len(neutron_data.index)=}')
                print('Заглушка для бага, где после корректировки данных по давлению. Они все равно плохи.')
                corr_pressure_data = corr_pressure_data[:len(neutron_data.index)]

            proccessing_pressure = self.proccessing_pressure_choice(corr_pressure_data)

            make_report_neutron(start_date=start_date, end_date=end_date, report_path=report_path,
                                picture_path=picture_path, neutron_data=neutron_data, pressure_data=corr_pressure_data,
                                proccessing_pressure=proccessing_pressure, accessory_data=accessory_data)
        except PermissionError:
            print("Закройте предыдущую версию файла!")
        except DateError:
            DateError(start_date, end_date).ui_output_error()

    def proccessing_pressure_choice(self, pressure_data):
        if self.radioButton.isChecked():
            return 993
        return np.mean(pressure_data)


app = QtWidgets.QApplication([])
window = Passport()
window.show()
app.exec()

