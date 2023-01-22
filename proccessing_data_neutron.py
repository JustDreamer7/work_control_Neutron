import datetime
from collections import defaultdict

import pandas as pd
from scipy.optimize import curve_fit


class ProccessingNeutron:
    def __init__(self, df_data, pressure_data, default_pressure=993):
        self.n_data = df_data
        self.pressure_data = pressure_data
        self.default_pressure = default_pressure

    def period_processing_for_report(self, start_date, end_date):
        worktime_dict = defaultdict(list)
        break_dict = self.count_breaks()
        parameters_dict = defaultdict(list)
        for det in range(1, 5):

            n_fit_params, n_fit_line = self.count_parameters(det, 'Nn')
            noise_fit_params, noise_fit_line = self.count_parameters(det, 'N_noise')

            parameters_dict['N_0'].append(n_fit_params[1])
            parameters_dict['N_0_noise'].append(noise_fit_params[1])

            parameters_dict['N_bar'].append(n_fit_params[0] / n_fit_params[1] * 100)
            parameters_dict['N_bar_noise'].append(noise_fit_params[0] / noise_fit_params[1] * 100)

            parameters_dict['B_factor'].append(n_fit_params[0])
            parameters_dict['B_factor_noise'].append(noise_fit_params[0])

            parameters_dict['fit_line_noise'].append(noise_fit_line)
            parameters_dict['fit_line'].append(n_fit_line)

            parameters_dict['correction_for_n'].append([(x - self.default_pressure) * n_fit_params[0] if x != 0 else 0
                                                        for x in self.pressure_data])
            parameters_dict['correction_for_noise'].append([(x - self.default_pressure) * noise_fit_params[0]
                                                            if x != 0 else 0 for x in self.pressure_data])
            for single_date in pd.date_range(start_date, end_date):
                worktime_dict['Date'].append(single_date)
                single_n_data = self.n_data[self.n_data['date'] == single_date].reset_index(drop=True)

                if len(single_n_data) == 0:
                    worktime_dict[f'Worktime_{det}'].append(0.00)
                    continue

                worktime_dict[f'Worktime_{det}'].append(self.count_worktime(single_n_data, det))

        worktime_frame = pd.DataFrame(worktime_dict)
        break_frame = pd.DataFrame(break_dict)

        return worktime_frame, break_frame, parameters_dict

    @staticmethod
    def count_worktime(n_file, det):
        return round((len(n_file.index) - len(
            n_file[(n_file[f'Nn{det}'] == 0) & (n_file[f'N_noise{det}'] == 0)])) * 5 / 60, 2)

    def count_breaks(self):
        breaks_dict = defaultdict(list)
        for det in range(1, 5):
            if len(self.n_data[(self.n_data[f'Nn{det}'] == 0) & (self.n_data[f'N_noise{det}'] == 0)]) != 0:
                worktime = self.n_data[
                    (self.n_data[f'Nn{det}'] != 0) & (self.n_data[f'N_noise{det}'] != 0)].reset_index(drop=True)
                if self.n_data['datetime'][0] != worktime['datetime'][0]:
                    breaks_dict['detector'].append(det)
                    breaks_dict['StartDate'].append(self.n_data['date'][0])
                    breaks_dict['EndDate'].append(worktime['date'][0])
                    breaks_dict['StartTime'].append(self.n_data['time'][0])
                    breaks_dict['EndTime'].append(worktime['time'][0])
                time_difference = worktime['datetime'].diff()
                for i in range(1, len(time_difference)):
                    if time_difference[i] > datetime.timedelta(minutes=6):
                        breaks_dict['detector'].append(det)
                        breaks_dict['StartDate'].append(worktime['date'][i - 1])
                        breaks_dict['EndDate'].append(worktime['date'][i])
                        breaks_dict['StartTime'].append(worktime['time'][i - 1])
                        breaks_dict['EndTime'].append(worktime['time'][i])
                if self.n_data['datetime'][len(self.n_data) - 1] != worktime['datetime'][len(worktime) - 1]:
                    breaks_dict['detector'].append(det)
                    breaks_dict['StartDate'].append(worktime['date'][len(worktime) - 1])
                    breaks_dict['EndDate'].append(self.n_data['date'][len(worktime) - 1])
                    breaks_dict['StartTime'].append(worktime['time'][len(worktime) - 1])
                    breaks_dict['EndTime'].append(self.n_data['time'][len(worktime) - 1])
        return breaks_dict

    def count_parameters(self, det, type_of_impulse):
        corr_pressure = [self.pressure_data[idx] for idx in
                         self.n_data[self.n_data[type_of_impulse + f'{det}'] != 0].index]

        def linear(x, a, b):
            return a * x + b

        fit_params, param_cov = curve_fit(linear, [x - self.default_pressure for x in corr_pressure],
                                          self.n_data[self.n_data[type_of_impulse + f'{det}'] != 0][
                                              type_of_impulse + f'{det}'])
        fit_line = [y * fit_params[0] + fit_params[1] for y in [x - self.default_pressure for x in corr_pressure]]
        return fit_params, fit_line


if __name__ == "__main__":
    from file_reader.neutron_file_reader import NeutronFileReader

    concat_df = NeutronFileReader.preparing_data(start_date=datetime.date(2020, 1, 1),
                                                 end_date=datetime.date(2020, 1, 3),
                                                 path_to_files='D:\\Neutron')
    # processing = ProccessingNeutron(concat_df)
    # worktime_fr, break_fr = processing.period_processing_for_report(start_date=datetime.date(2020, 1, 1),
    #                                                                 end_date=datetime.date(2020, 1, 3))
    # print(worktime_fr)
    # print(break_fr)
