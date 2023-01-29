import datetime
import pathlib
from collections import defaultdict

import numpy as np
import pandas as pd

from file_reader.abs_file_reader import FileReader


# from abs_file_reader import FileReader


class PressureFileReader(FileReader):
    def __init__(self, single_month, path_to_files):
        self._path_to_files = path_to_files
        self.single_month = single_month
        self._file_name = f'Press{self.single_month.year}_{self.single_month.month:02}.dat'
        self._columns = ['date', 'time', 'PD', 'TD', 'P_datch', 'Temper']

    @property
    def path_to_files(self):
        return self._path_to_files

    @property
    def file_name(self):
        return self._file_name

    @property
    def columns(self):
        return self._columns

    def making_file_path(self, file_directory):
        file_path = pathlib.PurePath(self.path_to_files, file_directory, self.file_name)
        return file_path

    def reading_file(self):
        pressure_file_path = self.making_file_path(file_directory='pressure')
        pressure_file = pd.read_csv(pressure_file_path,
                                    sep=r'\s', header=None,
                                    skipinitialspace=True, index_col=False,
                                    engine='python')
        pressure_file = pressure_file.drop(0).reset_index(drop=True)  # Убрать первый столбец с колонками, который
        # явно прописан
        pressure_file = pressure_file[pressure_file.notnull()].dropna(axis='columns')
        pressure_file.columns = self.columns
        pressure_file['date'] = pd.to_datetime(pressure_file['date'], format='%d.%m.%Y').dt.date
        pressure_file['time'] = pd.to_datetime(
            pressure_file['time']).dt.time  # Формат с датой и временем и работающим timedelta
        pressure_file['datetime'] = [datetime.datetime.combine(date, time) for date, time in
                                     zip(pressure_file['date'], pressure_file['time'])]
        return pressure_file

    @staticmethod
    def finding_breaks(pressure_data):
        breaks_dict = defaultdict(list)

        time_difference = pressure_data['datetime'].diff()[1:]
        time_difference = time_difference[time_difference > datetime.timedelta(seconds=25)]
        for idx in time_difference.index:
            breaks_dict['StartDateTime'].append(pressure_data['datetime'][idx - 1])
            breaks_dict['EndDateTime'].append(pressure_data['datetime'][idx])
            breaks_dict['StartDate'].append(pressure_data['date'][idx - 1])
            breaks_dict['EndDate'].append(pressure_data['date'][idx])
            breaks_dict['StartTime'].append(pressure_data['time'][idx - 1])
            breaks_dict['EndTime'].append(pressure_data['time'][idx])
            breaks_dict['CuttingIdx'].append(idx)
        return breaks_dict

    @staticmethod
    def cutting_pressure_data(pressure_data, breaks):
        divided_pressure_data = []
        start_idx = 0
        for idx in breaks['CuttingIdx']:
            divided_pressure_data.append(pressure_data.iloc[start_idx:idx].reset_index(drop=True))
            start_idx = idx
        divided_pressure_data.append(pressure_data.iloc[start_idx:].reset_index(drop=True))
        return divided_pressure_data

    @staticmethod
    def cutting_neutron_data_from_pressure_data(neutron_data, pressure_data):
        breaks_dict = PressureFileReader.finding_breaks(pressure_data)
        if any(breaks_dict):
            for i, _ in enumerate(breaks_dict['StartDateTime']):
                neutron_data = neutron_data[(neutron_data['datetime'] <= breaks_dict['StartDateTime'][i]) | (
                        neutron_data['datetime'] + datetime.timedelta(minutes=5) >= breaks_dict['EndDateTime'][i])]
            neutron_data.reset_index(drop=True, inplace=True)
            return neutron_data
        return neutron_data

    # @staticmethod
    # def change_pressure_interval(data, neutron_data):
    #     counter, summator = 0, 0
    #     mean_pressure = []
    #     for i in range(len(data['time'])):
    #         counter += 1
    #         summator += data['P_datch'][i]
    #         if (data['time'][i].minute % 10 == 0 or data['time'][i].minute % 5 == 0) and counter > 7:
    #             mean_pressure.append(round(summator / counter / 0.75006156, 2))
    #             counter, summator = 0, 0
    #     mean_pressure.append(round(summator / counter / 0.75006156, 2))
    #     return mean_pressure

    @staticmethod
    def change_pressure_interval(pressure_data, neutron_data):
        mean_pressure = []
        for datetime_item in neutron_data['datetime']:
            mean_pressure.append(round(np.mean(pressure_data[(pressure_data['datetime'] <= datetime_item) & (
                    pressure_data['datetime'] >= datetime_item - datetime.timedelta(minutes=5))][
                                                   'P_datch']) / 0.75006156, 2))
        return mean_pressure

    # @staticmethod
    # def correct_pressure_data(pressure_data, neutron_data):
    #     breaks_dict = PressureFileReader.finding_breaks(pressure_data)
    #     print(breaks_dict)
    #     if any(breaks_dict):
    #         div_pressure_data = PressureFileReader.cutting_pressure_data(pressure_data, breaks_dict)
    #         mean_pressure_list = []
    #         for frame in div_pressure_data:
    #             single_break = pd.DataFrame(frame)
    #             mean_pressure = PressureFileReader.change_pressure_interval(single_break, neutron_data)
    #             mean_pressure_list.append(mean_pressure)
    #         corr_mean_result = mean_pressure_list[0]
    #         blank_len = []
    #         for i, _ in enumerate(breaks_dict['StartDateTime']):
    #             blank_len.append(
    #                 len(neutron_data.index) - len(
    #                     neutron_data[(neutron_data['datetime'] <= breaks_dict['StartDateTime'][i]) | (
    #                             neutron_data['datetime'] >= breaks_dict['EndDateTime'][i])].index))
    #         for i in range(1, len(mean_pressure_list)):
    #             corr_mean_result = corr_mean_result + [0] * blank_len[i - 1] + mean_pressure_list[i]
    #         return corr_mean_result  # на этом этапе длина нейтронной даты и даты урагана не совпадает,
    #         # так как в нейтронной дате есть еще предыдущий день и одно событие следующего
    #     return PressureFileReader.change_pressure_interval(pressure_data, neutron_data)

    @staticmethod
    def preparing_data(start_date, end_date, path_to_files):
        """Статический метод подготовки данных из n-файлов за определенный период для определенного кластера"""
        concat_n_df = pd.DataFrame()
        for single_month in pd.period_range(start=start_date, end=end_date, freq='M'):
            try:
                filereader = PressureFileReader(single_month=single_month, path_to_files=path_to_files)
                concat_n_df = pd.concat([concat_n_df, filereader.reading_file()], ignore_index=True)
            except FileNotFoundError:
                print(
                    f"File {path_to_files}/n_{single_month.month:02}-" +
                    f"{single_month.day:02}.{single_month.year - 2000:02}', does not exist")
        return concat_n_df[(concat_n_df['date'] >= start_date) & (concat_n_df['date'] <= end_date)].reset_index(
            drop=True)


if __name__ == "__main__":
    from neutron_file_reader import NeutronFileReader

    neut_concat_df = NeutronFileReader.preparing_data(start_date=datetime.date(2020, 1, 1),
                                                      end_date=datetime.date(2020, 1, 3),
                                                      path_to_files='D:\\Neutron')
    file_reader = PressureFileReader(path_to_files='D:\\Neutron', single_month=datetime.date(2020, 1, 1))
    print(issubclass(PressureFileReader, FileReader))
    concat_df = PressureFileReader.preparing_data(start_date=datetime.date(2020, 1, 1),
                                                  end_date=datetime.date(2020, 1, 3),
                                                  path_to_files='D:\\Neutron')
    print(file_reader.change_pressure_interval(concat_df, neut_concat_df))
