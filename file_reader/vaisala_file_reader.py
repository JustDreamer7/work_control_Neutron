# from abs_file_reader import FileReader
from file_reader.abs_file_reader import FileReader

import pandas as pd
import pathlib
import datetime


class VaisalaFileReader(FileReader):
    def __init__(self, single_date, path_to_files):
        self._path_to_files = path_to_files
        self.single_date = single_date
        self._file_name = f'Station02__SMSAWS__{self.single_date.year}{self.single_date.month:02}' + \
                          f'{self.single_date.day:02}.txt'
        self._columns = ['date', 'time', 'TA', 'RH', 'PR']

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
        vaisala_file_path = self.making_file_path(file_directory=f'{self.single_date.year}\\{self.single_date.month:02}')
        # Подумать, как настроить файл директори, чтобы от года к году перескакивало
        vaisala_file = pd.read_csv(vaisala_file_path,
                                   sep=r'\t', skipinitialspace=True, index_col=False,
                                   engine='python')
        vaisala_file['date'] = [item.split(" ")[0] for item in vaisala_file['TIME']]
        vaisala_file['time'] = [item.split(" ")[1] for item in vaisala_file['TIME']]
        del vaisala_file['TIME']
        vaisala_file = vaisala_file[['date', 'time', 'TA', 'RH', 'PR']]
        return self.check_time_index(vaisala_file)

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
                filereader = VaisalaFileReader(single_date=single_date, path_to_files=path_to_files)
                concat_n_df = pd.concat([concat_n_df, filereader.reading_file()], ignore_index=True)
            except FileNotFoundError:
                print(
                    f"File {path_to_files}/n_{single_date.month:02}-" +
                    f"{single_date.day:02}.{single_date.year - 2000:02}', does not exist")
        return concat_n_df


if __name__ == "__main__":
    file_reader = VaisalaFileReader(path_to_files='D:\\Neutron\\Vaisala\\Station02',
                                    single_date=datetime.date(2022, 1, 3))
    # print(file_reader.path_to_files)
    # print(file_reader.reading_file())
    print(issubclass(VaisalaFileReader, FileReader))
    concat_df = VaisalaFileReader.preparing_data(start_date=datetime.date(2022, 1, 1),
                                                 end_date=datetime.date(2022, 1, 3),
                                                 path_to_files='D:\\Neutron\\Vaisala\\Station02')
    print(concat_df)
