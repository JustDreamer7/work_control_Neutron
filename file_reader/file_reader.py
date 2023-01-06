import datetime
import pandas as pd
import pathlib


class FileReader:

    def __init__(self, single_date, path_to_files=''):
        self.path_to_files = path_to_files
        self.single_date = single_date
        self.pressure_file_name = f'Press{self.single_date.year}_{self.single_date.month:02}.dat'
        self.dt_file_name = f'4dt{self.single_date.month:02}-' + \
                            f'{self.single_date.day:02}.{self.single_date.year - 2000:02}'
        self.vaisala_file_name = f'Station02__SMSAWS__{self.single_date.year}{self.single_date.month:02}' + \
                                 f'{self.single_date.day:02}.txt'

    def __del__(self):
        pass

    def making_file_path(self, file_directory, file_name):
        file_path = pathlib.PurePath(self.path_to_files, file_directory, file_name)
        return file_path

    def reading_dt_file(self):
        dt_file_path = self.making_file_path(file_directory='dt', file_name=self.dt_file_name)
        dt_file = pd.read_csv(dt_file_path,
                              sep=r'\s[-]*\s*', header=None, skipinitialspace=True, index_col=False, engine='python')
        dt_file.dropna(axis=1, how='all', inplace=True)
        dt_file.columns = ['date', 'time'] + [f'Nn{i}' for i in range(1, 5)] + [f'N_noise{i}' for i in range(1, 5)] + [
            f'const_{i}' for i in range(1, 4)]
        return self.check_time_index(dt_file)

    def reading_pressure_file(self):
        pressure_file_path = self.making_file_path(file_directory='pressure', file_name=self.pressure_file_name)
        pressure_file = pd.read_csv(pressure_file_path,
                                    sep=r'\s', header=None,
                                    skipinitialspace=True, index_col=False,
                                    engine='python')
        pressure_file = pressure_file.drop(0).reset_index(drop=True)  # Убрать первый столбец с колонками, который
        # явно прописан
        pressure_file = pressure_file[pressure_file.notnull()].dropna(axis='columns')
        pressure_file.columns = ['date', 'time', 'PD', 'TD', 'P_datch', 'Temper']
        return pressure_file

    def reading_vaisala_file(self):
        vaisala_file_path = self.making_file_path(file_directory='Vaisala\\Station02\\2022\\10',
                                                  file_name=self.vaisala_file_name)  # file_directory переделать к хуям, а
        # лучше разделить file_reader вайсалы, урагана, нейтрона, так как установки независимы
        vaisala_file = pd.read_csv(vaisala_file_path,
                                   sep=r'\t', skipinitialspace=True, index_col=False,
                                   engine='python')
        vaisala_file['date'] = [item.split(" ")[0] for item in vaisala_file['TIME']]
        vaisala_file['time'] = [item.split(" ")[1] for item in vaisala_file['TIME']]
        del vaisala_file['TIME']
        vaisala_file = vaisala_file[['date', 'time', 'TA', 'RH', 'PR']]
        return self.check_time_index(vaisala_file)

    @staticmethod
    def concat_data(file_today, file_day_after, single_date, concat_n_df):
        file_today['date'] = [single_date.date()] * len(file_today.index)
        concat_n_df = pd.concat([concat_n_df, file_today], ignore_index=True)
        if any(file_day_after):
            file_day_after['date'] = [(single_date + datetime.timedelta(
                days=1)).date()] * len(file_day_after.index)
            concat_n_df = pd.concat([concat_n_df, file_day_after],
                                    ignore_index=True)
        return concat_n_df

    @staticmethod
    def check_time_index(file_data):
        file_data['time'] = pd.to_datetime(file_data['time'])  # Формат с датой и временем и работающим timedelta
        time_difference = file_data['time'].diff()
        file_data['time'] = file_data['time'].dt.time  # Формат только со временем, но теперь timedelta не работает.
        bad_end_time_index = time_difference[time_difference < datetime.timedelta(days=0)].index
        if any(bad_end_time_index):
            file_today = file_data[file_data.index < bad_end_time_index[0]]
            file_day_after = file_data[file_data.index >= bad_end_time_index[0]]
            return file_today, file_day_after
        return file_data, []

    @staticmethod
    def preparing_data(start_date, end_date, path_to_files):
        """Статический метод подготовки данных из n-файлов за определенный период для определенного кластера"""
        concat_n_df = pd.DataFrame()
        # concat_n_df = pd.DataFrame(columns=['Date', 'time', 'trigger'] + FileReader.__amp_n_cols)
        for single_date in pd.date_range(start_date - datetime.timedelta(days=1), end_date):
            # минус один день в timedelta, так как начальные события первого дня могут остаться в n-файле предыдущего
            # дня
            try:
                file_reader = FileReader(single_date=single_date, path_to_files=path_to_files)
                file_today, file_day_after = file_reader.reading_dt_file()
                # file_today, file_day_after = file_reader.reading_pressure_file()
                # file_today, file_day_after = file_reader.reading_vaisala_file()
                concat_n_df = file_reader.concat_data(file_today=file_today, file_day_after=file_day_after,
                                                      concat_n_df=concat_n_df, single_date=single_date)
            except FileNotFoundError:
                print(
                    f"File {path_to_files}/n_{single_date.month:02}-" +
                    f"{single_date.day:02}.{single_date.year - 2000:02}', does not exist")
        return concat_n_df


if __name__ == "__main__":
    file_reader = FileReader(path_to_files='D:\\Neutron', single_date=datetime.date(2020, 1, 1))
    concat_df = FileReader.preparing_data(start_date=datetime.date(2020, 1, 1), end_date=datetime.date(2020, 1, 1),
                                          path_to_files='D:\\Neutron')
    print(file_reader.reading_pressure_file())
    print(concat_df.dtypes)
    # print(file_reader.reading_dt_file().head(5))
    # print(file_reader.reading_dt_file().dtypes)
    # print(file_reader.reading_pressure_file().head(5))
    # print(file_reader.reading_pressure_file().dtypes)
    # print(file_reader.reading_vaisala_file().head(5))
    # print(file_reader.reading_vaisala_file().dtypes)

# Как вариант можно просто держать в переменной список колонок для датафрейма

# Нужно написать абстрактный класс, file_reader и адаптировать для нейтрона, угарана и вайсалы, или для угарана
# создать свой, так как данный за месяц.
