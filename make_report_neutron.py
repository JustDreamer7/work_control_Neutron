import datetime
import time
import warnings
import pandas as pd


def make_report_neutron(start_date, end_date, report_path, picture_path, concat_n_df_1, concat_n_df_2):
    t1 = time.time()

    warnings.filterwarnings(action='ignore')

    days_amount = len(pd.date_range(start_date, end_date))


