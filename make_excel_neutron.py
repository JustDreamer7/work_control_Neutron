import datetime
import pathlib
import time

import pandas as pd

from graph_drawer import GraphsDrawing
from proccessing_data_neutron import ProccessingNeutron


def csv_save_neutron_files(neutron_data, files_path, start_date, end_date, ascending=True):
    # Исправить колонки neutron_data
    for det in range(1, 5):
        neutron_file = neutron_data[['datetime', f'Nn{det}']].sort_values(f'Nn{det}', ascending=ascending)
        neutron_file.to_csv(
            pathlib.PurePath(files_path, str(start_date.year), f'Nn{det} - {"asc" if ascending else "desc"} '
                                                               f'- {start_date.month:02}-{start_date.day:02}-'
                                                               f'{end_date.month:02}-{end_date.day:02}.csv'),
            sep=';', index=False)

        noise_file = neutron_data[['datetime', f'N_noise{det}']].sort_values(f'N_noise{det}', ascending=ascending)
        noise_file.to_csv(
            pathlib.PurePath(files_path, str(start_date.year), f'N_noise{det} - {"asc" if ascending else "desc"} '
                                                               f'- {start_date.month:02}-{start_date.day:02}-'
                                                               f'{end_date.month:02}-{end_date.day:02}.csv'),
            sep=';', index=False)


def corr_files(neutron_data, pressure_data, vaisala_data, files_path, start_date, end_date):
    data = neutron_data.copy()
    data['P_mm-bar_N'] = neutron_data['P_mm_rt_st_N'] / 0.75006156
    data['P_mm-bar'] = pressure_data
    data['P_mm-rt_st'] = [round(x * 0.75006156, 2) for x in pressure_data]
    data['TA_vaisala'] = ['/'] * len(data.index)
    data['RH_vaisala'] = ['/'] * len(data.index)
    data['PR_vaisala'] = ['/'] * len(data.index)

    for n_idx, n_item in enumerate(data['datetime']):
        for v_idx, v_item in enumerate(vaisala_data['datetime']):
            if abs(v_item - n_item) <= datetime.timedelta(seconds=180):
                if data['TA_vaisala'][n_idx] != vaisala_data['TA'][v_idx] and vaisala_data['TA'][v_idx] != '/':
                    data.loc[n_idx, 'TA_vaisala'] = f" {vaisala_data['TA'][v_idx]}"
                if data['RH_vaisala'][n_idx] != vaisala_data['RH'][v_idx] and vaisala_data['RH'][v_idx] != '/':
                    data.loc[n_idx, 'RH_vaisala'] = f" {(vaisala_data['RH'][v_idx])}"
                if data['PR_vaisala'][n_idx] != vaisala_data['PR'][v_idx] and vaisala_data['PR'][v_idx] != '/':
                    data.loc[n_idx, 'PR_vaisala'] = f" {(vaisala_data['PR'][v_idx])}"
                vaisala_data = vaisala_data.drop(index=[v_idx]).reset_index(drop=True)
                break

    dcorr_data = data[['datetime', ] + [f'Nn{i}' for i in range(1, 5)] + [f'N_noise{i}' for i in range(1, 5)] +
                      ['P_mm_rt_st_N', 'TN', 'AH', 'P_mm-bar', 'P_mm-bar_N', 'TA_vaisala', 'RH_vaisala',
                       'PR_vaisala']]
    dcorr_data.columns = ['datetime'] + [f'CotR{i}' for i in range(1, 5)] + [f'CotRFC{i}' for i in range(1, 5)] + [
        'P_mm_rt_st_N', 'TN', 'AH', 'P_mm-bar', 'P_mm-bar_N', 'TA_vaisala', 'RH_vaisala', 'PR_vaisala']
    dcorr_data.to_csv(
        pathlib.PurePath(files_path, str(start_date.year), f'DCorr_{start_date.month:02}-{start_date.day:02}-'
                                                           f'{end_date.month:02}-{end_date.day:02}.csv'),
        sep=';', index=False)

    ndata_temp_all = data[
        ['datetime'] + [f'corr_Nn{i}' for i in range(1, 5)] + [f'corr_N_noise{i}' for i in range(1, 5)] +
        ['P_mm-bar', 'TA_vaisala']]
    ndata_temp_all.columns = ['datetime'] + [f'N_cor{i:02}' for i in range(1, 5)] + \
                             [f'N_cor_noise{i:02}' for i in range(1, 5)] + ['P_mm-bar', 'TA_vaisala']
    ndata_temp_all.to_csv(pathlib.PurePath(files_path, str(start_date.year), f'NDATA_Temp_All_{start_date.month:02}-'
                                                                             f'{start_date.day:02}-{end_date.month:02}-'
                                                                             f'{end_date.day:02}.csv'),
                          sep=';', index=False)


def make_excel_neutron(start_date, end_date, files_path, picture_path, neutron_data, pressure_data, vaisala_data,
                       proccessing_pressure):
    t1 = time.time()

    processing_inst = ProccessingNeutron(df_data=neutron_data, pressure_data=pressure_data,
                                         default_pressure=proccessing_pressure)

    graphs = GraphsDrawing(start_date=start_date, end_date=end_date,
                           path_to_pic=f'{picture_path}')

    graphs.change_design()

    worktime_frame, break_frame, parameters_dict = processing_inst.period_processing_for_report(
        start_date=start_date, end_date=end_date)

    graphs.pressure_graph(corr_pressure_data=parameters_dict['corr_pressure_n'],
                          neutron_data=neutron_data,
                          fit_line=parameters_dict['fit_line'],
                          type_of_impulse='Nn')
    graphs.pressure_graph(corr_pressure_data=parameters_dict['corr_pressure_noise'],
                          neutron_data=neutron_data,
                          fit_line=parameters_dict['fit_line_noise'],
                          type_of_impulse='N_noise')
    graphs.neutron_graph(neutron_data=neutron_data,
                         corr_for_neutron_data=parameters_dict['correction_for_n'],
                         pressure_data=pressure_data,
                         type_of_impulse='Nn')
    graphs.neutron_graph(neutron_data=neutron_data,
                         corr_for_neutron_data=parameters_dict['correction_for_noise'],
                         pressure_data=pressure_data,
                         type_of_impulse='N_noise')
    csv_save_neutron_files(neutron_data=neutron_data, files_path=files_path, start_date=start_date, end_date=end_date,
                           ascending=True)
    csv_save_neutron_files(neutron_data=neutron_data, files_path=files_path, start_date=start_date, end_date=end_date,
                           ascending=False)
    corr_files(neutron_data=neutron_data, pressure_data=pressure_data, vaisala_data=vaisala_data, files_path=files_path,
               start_date=start_date, end_date=end_date)

    print(time.time() - t1)
