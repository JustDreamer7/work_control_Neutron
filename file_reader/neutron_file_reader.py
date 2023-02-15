import datetime
import pathlib
from collections import defaultdict

# from abs_file_reader import FileReader
import pandas as pd

from file_reader.abs_file_reader import FileReader


class NeutronFileReader(FileReader):
    def __init__(self, single_date, path_to_files):
        self._path_to_files = path_to_files
        self.single_date = single_date
        self._file_name = f'4dt{self.single_date.month:02}-' + \
                          f'{self.single_date.day:02}.{self.single_date.year - 2000:02}'
        self._columns = ['date', 'time'] + [f'Nn{i}' for i in range(1, 5)] + [f'N_noise{i}' for i in range(1, 5)] + [
            'P_mm_rt_st_N', 'TN', 'AH']

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
        dt_file_path = self.making_file_path(file_directory='dt')
        dt_file = pd.read_csv(dt_file_path,
                              sep=r'\s[-]*\s*', header=None, skipinitialspace=True, index_col=False, engine='python')
        dt_file.dropna(axis=1, how='all', inplace=True)
        dt_file.columns = self.columns
        dt_file['date'] = pd.to_datetime(dt_file['date']).dt.date
        return self.check_time_index(dt_file)

    @staticmethod
    def finding_breaks(neutron_data):
        breaks_dict = defaultdict(list)
        time_difference = neutron_data['datetime'].diff()[1:]
        time_difference = time_difference[time_difference > datetime.timedelta(seconds=310)]
        for idx in time_difference.index:
            breaks_dict['StartDateTime'].append(neutron_data['datetime'][idx - 1])
            breaks_dict['EndDateTime'].append(neutron_data['datetime'][idx])
            breaks_dict['StartDate'].append(neutron_data['date'][idx - 1])
            breaks_dict['EndDate'].append(neutron_data['date'][idx])
            breaks_dict['StartTime'].append(neutron_data['time'][idx - 1])
            breaks_dict['EndTime'].append(neutron_data['time'][idx])
            breaks_dict['CuttingIdx'].append(idx)
        return breaks_dict

    @staticmethod
    def correct_neutron_data(neutron_data):
        breaks_dict = NeutronFileReader.finding_breaks(neutron_data)
        if any(breaks_dict):
            list_of_series = []
            for i, _ in enumerate(breaks_dict['StartDateTime']):
                time_diff = breaks_dict['EndDateTime'][i] - breaks_dict['StartDateTime'][i]
                time_diff_sec = time_diff.total_seconds()
                list_of_series.extend([pd.Series({'Nn1': 0, 'Nn2': 0, 'Nn3': 0, 'Nn4': 0, 'N_noise1': 0,
                                                  'N_noise2': 0, 'N_noise3': 0, 'N_noise4': 0, 'const_1': 0,
                                                  'const_2': 0,
                                                  'const_3': 0, 'datetime': datetime_item,
                                                  'date': datetime.date(datetime_item.year,
                                                                        datetime_item.month,
                                                                        datetime_item.day),
                                                  'time': datetime.time(datetime_item.hour,
                                                                        datetime_item.minute,
                                                                        datetime_item.second)}) for datetime_item in
                                       [(breaks_dict['StartDateTime'][i] + datetime.timedelta(minutes=x)) for x in
                                        range(5, int(time_diff_sec / 60) + 1, 5)]])
            neutron_data = neutron_data.append(list_of_series, ignore_index=True)
            neutron_data.sort_values(by='datetime', inplace=True)
            neutron_data.reset_index(drop=True, inplace=True)
            return neutron_data
        return neutron_data

    @staticmethod
    def cutting_pressure_data_from_neutron_data(neutron_data, pressure_data):
        breaks_dict = NeutronFileReader.finding_breaks(neutron_data)
        if any(breaks_dict):
            for i, _ in enumerate(breaks_dict['StartDateTime']):
                pressure_data = pressure_data[(pressure_data['datetime'] <= breaks_dict['StartDateTime'][i]) | (
                        pressure_data['datetime'] >= breaks_dict['EndDateTime'][i] - datetime.timedelta(minutes=5))]
            pressure_data.reset_index(drop=True, inplace=True)
            return pressure_data
        return pressure_data

    @staticmethod
    def check_time_index(file_data):
        file_data['time'] = pd.to_datetime(file_data['time'])  # Формат с датой и временем и работающим timedelta
        time_difference = file_data['time'].diff()
        file_data['time'] = file_data['time'].dt.time  # Формат только со временем, но теперь timedelta не работает.
        bad_end_time_index = time_difference[time_difference < datetime.timedelta(days=0)].index
        if any(bad_end_time_index):
            file_today = file_data[file_data.index < bad_end_time_index[0]]
            file_day_after = file_data[file_data.index >= bad_end_time_index[0]]
            file_day_after['date'] = [file_day_after['date'].item() + datetime.timedelta(
                days=1)] * len(file_day_after.index)
            file_data = pd.concat([file_today, file_day_after], ignore_index=True)
        file_data['datetime'] = [datetime.datetime.combine(date, time) for date, time in
                                 zip(file_data['date'], file_data['time'])]
        return file_data

    # @staticmethod
    # def change_neutron_data_to_zero(neutron_data, pressure_breaks_dict):
    #     for det in range(1, 5):
    #         for i, _ in enumerate(pressure_breaks_dict['StartDateTime']):
    #             neutron_data[f'Nn{det}'] = neutron_data[f'Nn{det}'].where(
    #                 (neutron_data['datetime'] < pressure_breaks_dict['StartDateTime'][i]) | (
    #                         neutron_data['datetime'] > pressure_breaks_dict['EndDateTime'][i]), 0)
    #         for i, _ in enumerate(pressure_breaks_dict['StartDateTime']):
    #             neutron_data[f'N_noise{det}'] = neutron_data[f'N_noise{det}'].where(
    #                 (neutron_data['datetime'] < pressure_breaks_dict['StartDateTime'][i]) | (
    #                         neutron_data['datetime'] > pressure_breaks_dict['EndDateTime'][i]), 0)

    @staticmethod
    def preparing_data(start_date, end_date, path_to_files):
        """Статический метод подготовки данных из n-файлов за определенный период для определенного кластера"""
        concat_n_df = pd.DataFrame()
        for single_date in pd.date_range(start_date - datetime.timedelta(days=1), end_date):
            # минус один день в timedelta, так как начальные события первого дня могут остаться в n-файле предыдущего
            # дня
            filereader = NeutronFileReader(single_date=single_date, path_to_files=path_to_files)
            try:
                concat_n_df = pd.concat([concat_n_df, filereader.reading_file()], ignore_index=True)
            except FileNotFoundError:
                print(f"File {filereader.making_file_path(file_directory='dt')}, does not exist")
        return concat_n_df[(concat_n_df['date'] >= start_date) & (concat_n_df['date'] <= end_date)].reset_index(
            drop=True)  # чтобы выровнять списки и фреймы по длине, так как в neutron_data есть один день
        # из до заданного периода и одно событие после заданного периода


if __name__ == "__main__":
    file_reader = NeutronFileReader(path_to_files='D:\\Neutron', single_date=datetime.date(2020, 1, 1))
    print(issubclass(NeutronFileReader, FileReader))
    concat_df = NeutronFileReader.preparing_data(start_date=datetime.date(2020, 1, 1),
                                                 end_date=datetime.date(2020, 1, 3),
                                                 path_to_files='D:\\Neutron')
    print(concat_df)
