#!/usr/bin/env python3
"""

This module helps creates a CSV file with data which is not assumed to be time aligned. 
The outputted csv is front and back filled to more easily compare values across topics at a given time.

"""
import sys
import dask.dataframe as dd
import pandas as pd
import matplotlib.pyplot as plt
import uuid
from icecream import ic
ic.configureOutput(includeContext=True)

def show_data_on_timeline(df:dd):
  df[['cmd_vel_final.linear.x', 'cmd_vel_final.linear.y']].resample('1m').mean().compute().plot()
  plt.show()

def save_merged_dask_dataframe_to_csv(df : dd, file_name: str = None):
  if (not file_name):
    file_name = uuid.uuid1()
    file_name = "TODO" # TODO FOR TESTING - write the file name from an output data name
  pandas_df = df.compute()
  # needing to compute dask df as a pandas df in order to avoid empty partition when using fillna
  pandas_df = pandas_df.ffill().bfill()
  pandas_df.to_csv(f"{file_name}.csv", index=True)

def merge_csvs_using_dask(input_csvs:'list[str]'):
  # gather csvs
  concat_li = []
  for f in input_csvs:
    tmp_df = dd.read_csv(f)
    concat_li.append(tmp_df)
  df = dd.concat(concat_li)
  # set time as index
  df["time"] = dd.to_datetime(df["time"])
  df = df.set_index("time")
  save_merged_dask_dataframe_to_csv(df)  

