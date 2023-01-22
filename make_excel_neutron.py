import time
import warnings

import pandas as pd


def csv_save_neutron_files(neutron_data, files_path, start_date, end_date, ascending=True):
    # Исправить колонки neutron_data
    for det in range(1, 5):
        neutron_file = neutron_data[['datetime', f'Nn{det}']].sort_values(f'Nn{det}', ascending=ascending)
        neutron_file.to_csv(
            f'{files_path}\\{start_date.year}\\Nn{det}- возрастание{start_date.month:02}-'
            f'{start_date.day:02}-{end_date.month:02}-{end_date.day:02}.csv', sep=';', index=False)

        noise_file = neutron_data[['datetime', f'N_noise{det}']].sort_values(f'N_noise{det}', ascending=ascending)
        noise_file.to_csv(
            f'{files_path}\\{start_date.year}\\N_noise{det}- возрастание{start_date.month:02}-'
            f'{start_date.day:02}-{end_date.month:02}-{end_date.day:02}.csv', sep=';', index=False)


def make_excel_neutron(start_date, end_date, files_path, picture_path, neutron_data, pressure_data, vaisala_data,
                       proccessing_pressure):
    t1 = time.time()

    warnings.filterwarnings(action='ignore')

    days_amount = len(pd.date_range(start_date, end_date))

    print(time.time() - t1)
