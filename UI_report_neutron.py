import datetime
import os
import warnings

import numpy as np
import pandas.errors
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
from dotenv import load_dotenv

load_dotenv()
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

        ui_file_drctry.lineEdit.setText(os.environ.get("PATH_NEUTRON_FILES"))
        ui_file_drctry.lineEdit_2.setText(os.environ.get("PATH_URAGAN_FILES"))
        ui_file_drctry.lineEdit_3.setText(os.environ.get("PATH_VAISALA_FILES"))
        ui_file_drctry.lineEdit_4.setText(os.environ.get("PATH_MASK_FILES"))

        ui_file_drctry.pushButton.clicked.connect(
            lambda: Ui_takeFiles.getFileDirectory(ui_file_drctry, 'PATH_NEUTRON_FILES'))
        ui_file_drctry.pushButton_2.clicked.connect(
            lambda: Ui_takeFiles.getFileDirectory(ui_file_drctry, 'PATH_URAGAN_FILES'))
        ui_file_drctry.pushButton_3.clicked.connect(
            lambda: Ui_takeFiles.getFileDirectory(ui_file_drctry, 'PATH_VAISALA_FILES'))
        ui_file_drctry.pushButton_4.clicked.connect(
            lambda: Ui_takeFiles.getFileDirectory(ui_file_drctry, 'PATH_MASK_FILES'))

        self.widget.show()

    def open_report_directory(self):
        # Возможно нужно переопределять self.widget, чтобы не лагало отображение
        ui_report_drctry = Ui_drctryChoice()
        ui_report_drctry.setupUi(self.widget)
        ui_report_drctry.lineEdit.setText(os.environ.get("PATH_NEUTRON_REPORT"))
        ui_report_drctry.pushButton.clicked.connect(lambda: Ui_drctryChoice.get_report_directory(ui_report_drctry))
        self.widget.show()

    def return_files_on_click(self):
        # описание работы кнопки получения данных для составления маски
        start_date = self.dateEdit.date().toPyDate()
        end_date = self.dateEdit_2.date().toPyDate()
        load_dotenv()
        try:
            if start_date > end_date:
                raise DateError(start_date, end_date)
            report_path = os.environ.get("PATH_NEUTRON_REPORT")
            file_neutron_data = os.environ.get("PATH_NEUTRON_FILES")
            file_uragan_pressure = os.environ.get("PATH_URAGAN_FILES")
            file_vaisala_pressure = os.environ.get("PATH_VAISALA_FILES")

            picture_path = report_path + '/without_mask_Pics'
            files_path = report_path + '/without_mask_N_files'
            self.create_direct_checker(picture_path)
            self.create_direct_checker(files_path)
            self.create_direct_checker(files_path+f'/{start_date.year}')
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
        load_dotenv()
        try:
            if start_date > end_date:
                raise DateError(start_date, end_date)
            report_path = os.environ.get("PATH_NEUTRON_REPORT")
            print(report_path)
            file_neutron_data = os.environ.get("PATH_NEUTRON_FILES")
            file_uragan_pressure = os.environ.get("PATH_URAGAN_FILES")
            file_mask = os.environ.get("PATH_MASK_FILES")

            picture_path = report_path + '/Pics'
            self.create_direct_checker(picture_path)
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
                except pandas.errors.ParserError as e:
                    print(e.args)
                    print(f'Проблемы с самим файлом, pandas не может распарсить')
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

    @staticmethod
    def create_direct_checker(direct_path):
        try:
            os.mkdir(direct_path)
        except OSError:
            print(f"Создать директорию {direct_path} не удалось")
        else:
            print(f"Успешно создана директория {direct_path}")


app = QtWidgets.QApplication([])
window = Passport()
window.show()
app.exec()
