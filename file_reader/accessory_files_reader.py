import os.path
import pathlib

import pandas as pd


class AccessoryFileReader:
    def __init__(self, path_to_files, start_date, end_date):
        self._path_to_files = path_to_files
        self.start_date = start_date
        self.end_date = end_date
        self.single_date = end_date
        self.columns = [f'det_{i}' for i in range(1, 5)]
        self.n_amp_columns = self.columns + [f'noise_{i}' for i in range(1, 5)]

    def making_file_path(self, file_directory, file_name):
        file_path = pathlib.PurePath(self._path_to_files, file_directory, file_name)
        date_range = pd.date_range(self.start_date, self.end_date).tolist()
        while not os.path.isfile(file_path):
            date_range.remove(self.single_date)
            self.single_date = date_range[-1]
            print(f"File {file_path} doesn't exist")
            file_path = pathlib.PurePath(self._path_to_files, file_directory, file_name)
        return file_path

    def r_file_reader(self):
        r_file_name = f'4R{self.single_date.month:02}-{self.single_date.day:02}.{self.single_date.year - 2000:02}'
        try:
            r_file_path = self.making_file_path(file_directory='sp',
                                                file_name=r_file_name)
            r_distribution = pd.read_csv(r_file_path, sep=' ', header=None, skipinitialspace=True, index_col=0)
            r_distribution.dropna(axis=1, how='all', inplace=True)
            r_distribution.columns = self.columns
            return r_distribution
        except IndexError:
            return None

    def front_time_data_reader(self):
        ft_file_name = f'4Tf{self.single_date.month:02}-{self.single_date.day:02}.{self.single_date.year - 2000:02}'
        try:
            ft_file_path = self.making_file_path(file_directory='sp',
                                                 file_name=ft_file_name)
            front_time_data = pd.read_csv(ft_file_path, sep=' ', header=None, skipinitialspace=True, index_col=0)
            front_time_data.dropna(axis=1, how='all', inplace=True)
            front_time_data.columns = self.columns
            return front_time_data
        except IndexError:
            return None

    def n_amp_data_reader(self):
        try:
            n_amp_file_name = f'4sp{self.single_date.month:02}-{self.single_date.day:02}' \
                              f'.{self.single_date.year - 2000:02}'
            n_amp_file_path = self.making_file_path(file_directory='sp',
                                                    file_name=n_amp_file_name)
            n_amp_time_data = pd.read_csv(n_amp_file_path, sep=' ', header=None, skipinitialspace=True, index_col=0)
            n_amp_time_data.dropna(axis=1, how='all', inplace=True)
            n_amp_time_data.columns = self.n_amp_columns
            return n_amp_time_data
        except IndexError:
            return None
