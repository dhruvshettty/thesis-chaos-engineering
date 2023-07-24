#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script uses the statsmodels library to perform Granger Causality tests to check if one time series is 
useful in forecasting another.

Author: dhruvshetty213@gmail.com
"""

import os
import pandas as pd
import numpy as np
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller, grangercausalitytests


def perform_granger_causality_tests(file_path, columns_to_exclude):
    """
    Perform Granger Causality tests on the time series data in the given file.

    Parameters:
        file_path (str): The location of the CSV file containing the time series data.
        columns_to_exclude (list): The list of column names to exclude from the data before performing tests.

    Returns:
        dict: A dictionary where the keys are the names of the columns that Granger cause the 'apdex' column,
              and the values are the counts of such occurrences.
    """
    data = pd.read_csv(file_path, index_col=0, parse_dates=True)
    data_caus = data.drop(columns_to_exclude, axis=1).copy()

    causality_counts = {}

    for column in data_caus.columns.drop("apdex"):
        data_orig = data[[column, "apdex"]].copy()

        result_adf = adfuller(data_orig[column])
        if result_adf[1] >= 0.05:
            data_orig = data_orig.diff().dropna()

        model = VAR(data_orig)
        results = model.fit(maxlags=20, ic='aic')

        if results.k_ar > 0:
            result = grangercausalitytests(data_orig, maxlag=results.k_ar, verbose=False)
            p_values = [round(result[i+1][0]['ssr_ftest'][1],4) for i in range(results.k_ar)]
            min_p_value = np.min(p_values)
            if min_p_value < 0.05:
                if column in causality_counts:
                    causality_counts[column] += 1
                else:
                    causality_counts[column] = 1

    return causality_counts


if __name__ == "__main__":
    # Folder path
    folder_path = '/path/to/datasets'

    # Get a list of all file paths in the folder
    file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]

    columns_to_exclude = ['tsr', 'errors', 'cpu']   # Replace cpu with io for IO experiments dataset

    # Run Granger causality test for each file
    causality_counts_aggregate = {}
    for file_path in file_paths:
        causality_counts = perform_granger_causality_tests(file_path, columns_to_exclude)
        for key, value in causality_counts.items():
            if key in causality_counts_aggregate:
                causality_counts_aggregate[key] += value
            else:
                causality_counts_aggregate[key] = value

    print(causality_counts_aggregate)
