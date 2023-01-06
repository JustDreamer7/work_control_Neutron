from file_reader.abs_file_reader import FileReader
import pandas as pd
import pathlib
import datetime


class NeutronFileReader(FileReader):
    def __init__(self, single_date, path_to_files):
        self._path_to_files = path_to_files
        self.single_date = single_date
        self._file_name = f'4dt{self.single_date.month:02}-' + \
                          f'{self.single_date.day:02}.{self.single_date.year - 2000:02}'
        self._columns = ['date', 'time'] + [f'Nn{i}' for i in range(1, 5)] + [f'N_noise{i}' for i in range(1, 5)] + [
            f'const_{i}' for i in range(1, 4)]

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
            return pd.concat([file_today, file_day_after], ignore_index=True)
        return file_data

    @staticmethod
    def preparing_data(start_date, end_date, path_to_files):
        """Статический метод подготовки данных из n-файлов за определенный период для определенного кластера"""
        concat_n_df = pd.DataFrame()
        for single_date in pd.date_range(start_date - datetime.timedelta(days=1), end_date):
            # минус один день в timedelta, так как начальные события первого дня могут остаться в n-файле предыдущего
            # дня
            try:
                filereader = NeutronFileReader(single_date=single_date, path_to_files=path_to_files)
                concat_n_df = pd.concat([concat_n_df, filereader.reading_file()], ignore_index=True)
            except FileNotFoundError:
                print(
                    f"File {path_to_files}/n_{single_date.month:02}-" +
                    f"{single_date.day:02}.{single_date.year - 2000:02}', does not exist")
        return concat_n_df


if __name__ == "__main__":
    file_reader = NeutronFileReader(path_to_files='D:\\Neutron', single_date=datetime.date(2020, 1, 1))
    print(issubclass(NeutronFileReader, FileReader))
    concat_df = NeutronFileReader.preparing_data(start_date=datetime.date(2020, 1, 1),
                                                 end_date=datetime.date(2020, 1, 3),
                                                 path_to_files='D:\\Neutron')
    print(concat_df)
