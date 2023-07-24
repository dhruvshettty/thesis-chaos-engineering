#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script calculates and displays the Pearson and Spearman correlations of the
specified metrics ('tsr', 'apdex') across multiple data files.

Author: dhruvshetty213@gmail.com
"""

import numpy as np
import pandas as pd
import os
import logging

# Configuration
config = {
    'folder_path': '/path/to/datasets/',
    'metrics': ['tsr', 'apdex'],
    'metrics_to_exclude': ['tsr', 'apdex', 'cpu'],
}

# Logging config
logging.basicConfig(level=logging.INFO)

def get_file_paths(folder_path):
    """
    Returns a list of all file paths in the specified folder.
    """
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

def calculate_correlation(file_paths, metric):
    """
    Calculates and logs the Pearson and Spearman correlations of the specified metric
    across multiple data files.
    """
    # Rest of the columns apart from the one for which the correlation test is done should be removed
    columns_to_exclude = config['metrics_to_exclude'].copy()
    columns_to_exclude.remove(metric)

    pearson_series_list = []
    spearman_series_list = []

    for file_path in file_paths:
        data = pd.read_csv(file_path)
        if metric not in data.columns:
            logging.error(f"Metric '{metric}' not found in file {file_path}. Available columns are: {', '.join(data.columns)}.")
            return

        # Columns to visualize correlations
        data_corr = data.drop(columns_to_exclude, axis=1)

        # Calculate correlation coefficients
        pearson_coeff = data_corr.corr(method='pearson')
        spearman_coeff = data_corr.corr(method='spearman')

        # Append the series (correlations with the metric) to the respective lists
        pearson_series_list.append(pearson_coeff[metric])
        spearman_series_list.append(spearman_coeff[metric])

    # Concatenate all the series along a new axis
    pearson_2d = np.stack([s.values for s in pearson_series_list])
    spearman_2d = np.stack([s.values for s in spearman_series_list])

    # Compute the mean, min and max correlation along the new axis
    pearson_mean = np.mean(pearson_2d, axis=0)
    spearman_mean = np.mean(spearman_2d, axis=0)

    pearson_min = np.min(pearson_2d, axis=0)
    spearman_min = np.min(spearman_2d, axis=0)

    pearson_max = np.max(pearson_2d, axis=0)
    spearman_max = np.max(spearman_2d, axis=0)

    # Use index from one of the correlation series
    index = pearson_series_list[0].index

    # Convert the numpy arrays back to series
    pearson_mean_s = pd.Series(pearson_mean, index=index)
    spearman_mean_s = pd.Series(spearman_mean, index=index)

    pearson_min_s = pd.Series(pearson_min, index=index)
    spearman_min_s = pd.Series(spearman_min, index=index)

    pearson_max_s = pd.Series(pearson_max, index=index)
    spearman_max_s = pd.Series(spearman_max, index=index)

    # Log the results
    logging.info(f"Pearson mean correlation with '{metric}':\n{pearson_mean_s}")
    logging.info(f"Spearman mean correlation with '{metric}':\n{spearman_mean_s}")
    logging.info(f"Pearson min correlation with '{metric}':\n{pearson_min_s}")
    logging.info(f"Spearman min correlation with '{metric}':\n{spearman_min_s}")
    logging.info(f"Pearson max correlation with '{metric}':\n{pearson_max_s}")
    logging.info(f"Spearman max correlation with '{metric}':\n{spearman_max_s}")

def main():
    file_paths = get_file_paths(config['folder_path'])

    if not file_paths:
        logging.error(f"No files found in {config['folder_path']}. Please check the folder path.")
        return

    for metric in config['metrics']:
        calculate_correlation(file_paths, metric)

if __name__ == "__main__":
    main()
