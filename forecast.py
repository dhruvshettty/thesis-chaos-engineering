#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script uses the Multivariate Vector Autoregression model
from the Statsmodels package to forecast Apdex scores.

Author: dhruvshetty213@gmail.com
"""
import os
import pandas as pd
from statsmodels.tsa.api import VAR
from sklearn.metrics import r2_score, confusion_matrix
from sklearn.preprocessing import MinMaxScaler

COLUMN_EXCLUSION = ['tsr', 'errors', 'cpu']  # Change 'cpu' to 'io' for I/O experiments
FOLDER_PATH = '/path/to/datasets'
TEST_SIZE = 6
THRESHOLD = 0.6

def read_and_preprocess(file_path):
    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
    return df.drop(COLUMN_EXCLUSION, axis=1)

def scale_data(train, test):
    scalers = {}
    for column in train.columns:
        scaler = MinMaxScaler(feature_range=(0, 1))
        train[column] = scaler.fit_transform(train[[column]])
        test[column] = scaler.transform(test[[column]])
        scalers[column] = scaler
    return train, test, scalers['apdex']

def fit_VAR_model(train):
    model = VAR(train)
    results = model.fit(maxlags=TEST_SIZE, ic='aic')
    return results, results.k_ar

def forecast_VAR(results, lag_order, train):
    prior = train.iloc[-lag_order:][train.columns].to_numpy()
    return results.forecast(prior, TEST_SIZE)

def compute_r2(df, train_idx, test_idx, lag_order):
    y_pred_train = df.loc[train_idx, 'Train Pred Apdex']
    y_true_train = df.loc[train_idx, 'ScaledApdex'].iloc[lag_order:]
    print("Apdex VAR Train R^2:", r2_score(y_true_train, y_pred_train))

    y_pred_test = df.loc[test_idx, 'Test Pred Apdex']
    y_true_test = df.loc[test_idx, 'ScaledApdex']
    print("Apdex VAR Test R^2:", r2_score(y_true_test, y_pred_test))

def plot_data(df):
    plot_cols = ['ScaledApdex', 'Train Pred Apdex', 'Test Pred Apdex']
    ax = df.iloc[-100:][plot_cols].plot(figsize=(15, 5))
    ax.set_title(f"True value: {any_true_below_threshold}, Predicted value: {any_pred_below_threshold}")

def main():
    file_paths = [os.path.join(FOLDER_PATH, f) for f in os.listdir(FOLDER_PATH)]
    aggregated_y_pred = []
    aggregated_y_true = []

    for count, file_path in enumerate(file_paths):
        df = read_and_preprocess(file_path)
        
        train = df.iloc[:-TEST_SIZE].copy()
        test = df.iloc[-TEST_SIZE:].copy()
        train, test, scaler = scale_data(train, test)
        
        train_idx = df.index <= train.index[-1]
        test_idx = df.index > train.index[-1]
        results, lag_order = fit_VAR_model(train)
        forecast = forecast_VAR(results, lag_order, train)
        
        df.loc[train_idx, 'Train Pred Apdex'] = results.fittedvalues['apdex']
        df.loc[test_idx, 'Test Pred Apdex'] = forecast[:,6]
        
        compute_r2(df, train_idx, test_idx, lag_order)
        
        y_pred_test = df.loc[test_idx, 'Test Pred Apdex']
        y_true_test = df.loc[test_idx, 'ScaledApdex']
        
        y_pred_original = scaler.inverse_transform(y_pred_test.values.reshape(-1, 1))
        y_true_original = scaler.inverse_transform(y_true_test.values.reshape(-1, 1))
        
        any_true_below_threshold = int((y_true_original < THRESHOLD).any())
        any_pred_below_threshold = int((y_pred_original < THRESHOLD).any())

        plot_data(df)
        aggregated_y_true.append(any_true_below_threshold)
        aggregated_y_pred.append(any_pred_below_threshold)

    matrix = confusion_matrix(aggregated_y_true, aggregated_y_pred)
    print(matrix)

if __name__ == "__main__":
    main()
