import pathlib
import random

import pandas as pd


class MaskFileReader:
    def __init__(self, path_to_files, start_date, end_date):
        self._path_to_files = path_to_files
        self.single_date = random.choice(pd.date_range(start_date, end_date))
        self.columns = [f'det_{i}' for i in range(1, 5)]
        self.n_amp_columns = self.columns + [f'noise_{i}' for i in range(1, 5)]

    def making_file_path(self, file_directory, file_name):
        file_path = pathlib.PurePath(self._path_to_files, file_directory, file_name)
        return file_path

    def r_file_reader(self):
        r_file_name = f'4R{self.single_date.month:02}-{self.single_date.day:02}.{self.single_date.year - 2000:02}'
        r_file_path = self.making_file_path(file_directory='sp',
                                            file_name=r_file_name)
        r_distribution = pd.read_csv(r_file_path, sep=' ', header=None, skipinitialspace=True, index_col=0)
        r_distribution.dropna(axis=1, how='all', inplace=True)
        r_distribution.columns = self.columns
        return r_distribution

    def front_time_data_reader(self):
        ft_file_name = f'4Tf{self.single_date.month:02}-{self.single_date.day:02}.{self.single_date.year - 2000:02}'
        ft_file_path = self.making_file_path(file_directory='sp',
                                            file_name=ft_file_name)
        front_time_data = pd.read_csv(ft_file_path, sep=' ', header=None, skipinitialspace=True, index_col=0)
        front_time_data.dropna(axis=1, how='all', inplace=True)
        front_time_data.columns = self.columns
        return front_time_data

    def n_amp_data_reader(self):
        n_amp_file_name = f'4sp{self.single_date.month:02}-{self.single_date.day:02}.{self.single_date.year - 2000:02}'
        n_amp_file_path = self.making_file_path(file_directory='sp',
                                             file_name=n_amp_file_name)
        n_amp_time_data = pd.read_csv(n_amp_file_path, sep=' ', header=None, skipinitialspace=True, index_col=0)
        n_amp_time_data.dropna(axis=1, how='all', inplace=True)
        n_amp_time_data.columns = self.n_amp_columns
        return n_amp_time_data

