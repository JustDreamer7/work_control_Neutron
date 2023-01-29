import pathlib

import pandas as pd


class MaskFileReader:
    def __init__(self, path_to_files, detector):
        self._path_to_files = path_to_files
        self._detector = detector
        self._file_name = f'Maska_detAll{self._detector}.dat'

    @property
    def path_to_files(self):
        return self._path_to_files

    @property
    def file_name(self):
        return self._file_name

    def making_file_path(self):
        file_path = pathlib.PurePath(self.path_to_files, self.file_name)
        return file_path

    def reading_file(self):
        mask_file_path = self.making_file_path()
        mask_file = pd.read_csv(mask_file_path, sep='\t', names=['start_datetime', 'end_datetime'],
                                skipinitialspace=True)
        mask_without_periods = mask_file.fillna(0)[mask_file.fillna(0)['end_datetime'] == 0][
            ['start_datetime']].reset_index(drop=True)
        period_mask = mask_file.dropna().reset_index(drop=True)

        mask_without_periods['start_datetime'] = pd.to_datetime(mask_without_periods['start_datetime'],
                                                                format='%d.%m.%Y %H:%M:%S')
        period_mask['start_datetime'] = pd.to_datetime(period_mask['start_datetime'],
                                                       format='%d.%m.%Y %H:%M:%S')
        period_mask['end_datetime'] = pd.to_datetime(period_mask['end_datetime'],
                                                     format='%d.%m.%Y %H:%M:%S')
        return period_mask, mask_without_periods

    @staticmethod
    def correct_neutron_data(neutron_data, mask_without_periods, period_mask, detector):
        for item in mask_without_periods['start_datetime']:
            neutron_data.loc[neutron_data[(neutron_data['datetime'].isin([item]))].index, f'Nn{detector}'] = 0
            neutron_data.loc[neutron_data[(neutron_data['datetime'].isin([item]))].index, f'N_noise{detector}'] = 0

        for item in range(len(period_mask.index)):
            neutron_data[f'Nn{detector}'] = neutron_data[f'Nn{detector}'].where(
                (neutron_data['datetime'] < period_mask['start_datetime'][item]) | (
                        neutron_data['datetime'] > period_mask['end_datetime'][item]), 0)
            neutron_data[f'N_noise{detector}'] = neutron_data[f'N_noise{detector}'].where(
                (neutron_data['datetime'] < period_mask['start_datetime'][item]) | (
                        neutron_data['datetime'] > period_mask['end_datetime'][item]), 0)
        return neutron_data


if __name__ == "__main__":
    file_reader = MaskFileReader(path_to_files='D:\\Neutron', detector=1)
    print(file_reader.reading_file())
