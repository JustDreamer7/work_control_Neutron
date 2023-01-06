import datetime
import pathlib
from collections import defaultdict

import pandas as pd

from abs_file_reader import FileReader


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

        return pressure_file

    @staticmethod
    def finding_breaks(pressure_data):
        breaks_dict = defaultdict(list)
        pressure_data['datetime'] = [datetime.datetime.combine(date, time) for date, time in
                                     zip(pressure_data['date'], pressure_data['time'])]
        time_difference = pressure_data['datetime'].diff()[1:]
        time_difference = time_difference[time_difference > datetime.timedelta(seconds=25)]
        for idx in time_difference.index:
            breaks_dict['StartDate'].append(pressure_data['date'][idx - 1])
            breaks_dict['EndDate'].append(pressure_data['date'][idx])
            breaks_dict['StartTime'].append(pressure_data['time'][idx - 1])
            breaks_dict['EndTime'].append(pressure_data['time'][idx])
            breaks_dict['CuttingIdx'].append(pressure_data['time'][idx])

        return breaks_dict

    @staticmethod
    def cutting_pressure_data(pressure_data, breaks):
        divided_pressure_data = []
        start_idx = 0
        for idx in breaks['CuttingIdx']:
            divided_pressure_data.append(pressure_data.iloc[start_idx:idx].reset_index(drop=True))
            start_idx = idx
        return divided_pressure_data

    @staticmethod
    def change_pressure_interval(data):
        counter = 0
        summator = 0
        mean_pressure = []
        for i in range(len(data['time'])):
            counter += 1
            summator += data['P_datch'][i]
            if (data['time'][i].minute % 10 == 0 or data['time'][i].minute % 5 == 0) and counter > 7:
                mean_pressure.append(round(summator / counter / 0.75006156, 2))
                summator = 0
                counter = 0
        mean_pressure.append(round(summator / counter / 0.75006156, 2))
        return mean_pressure

    def correct_pressure_data(self, pressure_data):
        breaks_dict = self.finding_breaks(pressure_data)
        if any(breaks_dict):
            div_pressure_data = self.cutting_pressure_data(pressure_data, breaks_dict)
            mean_pressure_list = []
            for frame in div_pressure_data:
                single_break = pd.DataFrame(frame)
                mean_pressure = self.change_pressure_interval(single_break)
                mean_pressure_list.append(mean_pressure)
            corr_mean_result = mean_pressure_list[0]
            # for i in range(1, len(mean_pressure_list)):
            #     corr_mean_result = corr_mean_result + [0] * cutting_len[i - 1] + mean_pressure_list[i]
            return corr_mean_result
        return self.change_pressure_interval(pressure_data)

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
        return concat_n_df[(concat_n_df['date'] >= start_date) & (concat_n_df['date'] <= end_date)]


if __name__ == "__main__":
    file_reader = PressureFileReader(path_to_files='D:\\Neutron', single_month=datetime.date(2020, 1, 1))
    print(issubclass(PressureFileReader, FileReader))
    concat_df = PressureFileReader.preparing_data(start_date=datetime.date(2020, 1, 1),
                                                  end_date=datetime.date(2020, 2, 3),
                                                  path_to_files='D:\\Neutron')
    print(file_reader.correct_pressure_data(concat_df))
