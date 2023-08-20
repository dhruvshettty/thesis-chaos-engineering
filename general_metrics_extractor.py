#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This is a general example script that shows querying the
Golden signals and Apdex score from the New Relic APM endpoint.

Author: dhruvshetty213@gmail.com
"""

import requests
import json
import os
import pandas as pd
from datetime import datetime, timezone, timedelta

# Constants
ENDPOINT = "https://api.eu.newrelic.com/graphql"
HEADERS = {'API-Key': os.environ.get('NEW_RELIC_API_KEY')}
ACCOUNT_ID = os.environ.get('ACCOUNT_ID')
APP_NAME = os.environ.get('APP_NAME')

def execute_query(query):
    """
    Execute the given NRQL query and return results.
    """
    response = requests.post(ENDPOINT, headers=HEADERS, json={"query": query})
    response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an error status code
    data = json.loads(response.content)
    return data['data']['actor']['account']['nrql']['results']

def create_dataframe_from_query(query, column_to_rename, new_column_name):
    """
    Create a dataframe from the provided NRQL query.
    """
    results = execute_query(query)
    df = pd.DataFrame(results)
    df = df.drop(['endTimeSeconds'], axis=1)
    df = df.rename(columns={column_to_rename: new_column_name})
    return df

def get_timeseries_query(metric, start, end, sample_rate, additional_conditions=""):
    """
    Get a timeseries query for the given metric and conditions.
    """
    return f"""
    {{
        actor {{
            account(id: {ACCOUNT_ID}) {{
                nrql(query: "FROM Transaction SELECT {metric} WHERE appName = '{APP_NAME}' {additional_conditions} SINCE '{start}' UNTIL '{end}' TIMESERIES {sample_rate}") {{
                    results
                }}
            }}
        }}
    }}
    """

# Example query for errors percentage from New Relic APM:
errors_query = get_timeseries_query("percentage(count(*), where error is true)", start, end, sample_rate, "AND transactionType = 'Web'")
df_errors = create_dataframe_from_query(errors_query, 'percentage', 'errors')
