import datetime
from collections import defaultdict

import pandas as pd


class ProccessingNeutron:
    def __init__(self, df_data):
        self.n_data = df_data

    def period_processing_for_report(self, start_date, end_date):
        worktime_dict = defaultdict(list)
        break_dict = self.count_breaks()
        for single_date in pd.date_range(start_date, end_date):
            worktime_dict['Date'].append(single_date)
            single_n_data = self.n_data[self.n_data['date'] == single_date].reset_index(drop=True)

            if len(single_n_data) == 0:
                for i in range(1, 5):
                    worktime_dict[f'Worktime_{i}'].append(0.00)
                continue

            worktime_day_list = list(self.count_worktime(single_n_data))

            for i in range(1, 5):
                worktime_dict[f'Worktime_{i}'].append(worktime_day_list[i - 1])

        worktime_frame = pd.DataFrame(worktime_dict)
        break_frame = pd.DataFrame(break_dict)

        return worktime_frame,break_frame

    @staticmethod
    def count_worktime(n_file):
        return (round((len(n_file.index) - len(
            n_file[(n_file[f'Nn{i}'] == 0) & (n_file[f'N_noise{i}'] == 0)])) * 5 / 60, 2) for i in range(1, 5))

    def count_breaks(self):
        self.n_data['datetime'] = [datetime.datetime.combine(date,time) for date, time in zip(self.n_data['date'], self.n_data['time'])]
        breaks_dict = defaultdict(list)
        for det in range(1, 5):
            if len(self.n_data[(self.n_data[f'Nn{det}'] == 0) & (self.n_data[f'N_noise{det}'] == 0)]) != 0:
                worktime = self.n_data[(self.n_data[f'Nn{det}'] != 0) & (self.n_data[f'N_noise{det}'] != 0)].reset_index(drop=True)
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
                        breaks_dict['StartTime'].append(worktime['time'][i-1])
                        breaks_dict['EndTime'].append(worktime['time'][i])
                if self.n_data['datetime'][len(self.n_data)-1] != worktime['datetime'][len(worktime)-1]:
                    breaks_dict['detector'].append(det)
                    breaks_dict['StartDate'].append(worktime['date'][len(worktime)-1])
                    breaks_dict['EndDate'].append(self.n_data['date'][len(worktime)-1])
                    breaks_dict['StartTime'].append(worktime['time'][len(worktime)-1])
                    breaks_dict['EndTime'].append(self.n_data['time'][len(worktime)-1])
        return breaks_dict


if __name__ == "__main__":
    from file_reader.neutron_file_reader import NeutronFileReader

    concat_df = NeutronFileReader.preparing_data(start_date=datetime.date(2020, 1, 1),
                                                 end_date=datetime.date(2020, 1, 3),
                                                 path_to_files='D:\\Neutron')
    processing = ProccessingNeutron(concat_df)
    worktime_fr, break_fr = processing.period_processing_for_report(start_date=datetime.date(2020, 1, 1),
                                                  end_date=datetime.date(2020, 1, 3))
    print(worktime_fr)
    print(break_fr)
