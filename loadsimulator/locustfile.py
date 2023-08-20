#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script is the entry point of the Locust load simulator used as part of this experiment.
A custom load shape is used to produce dynamic changes in user counts at random times to make
the validity of the collected data stochastic.

Author: dhruvshetty213@gmail.com
"""
import os
import numpy as np
from locust import events, LoadTestShape

class Config:
    INITIAL_USER_COUNT = 25
    INITIAL_SPAWN_RATE = 1
    MIN_USER_COUNT = 25
    MEAN_USER_COUNT = 50
    MAX_USER_COUNT = 75
    MIN_SPAWN_RATE = 1
    MEAN_SPAWN_RATE = 2
    MAX_SPAWN_RATE = 3
    MIN_TIME_INTERVAL_SECONDS = 60
    MEAN_TIME_INTERVAL_SECONDS = 150
    MAX_TIME_INTERVAL_SECONDS = 240

class AutoLoadTestShape(LoadTestShape):
    """
    A custom load test shape that generates random user counts and spawn rates at random time intervals.
    """

    def __init__(self, config=Config):
        super().__init__()
        self.user_count = config.INITIAL_USER_COUNT
        self.spawn_rate = config.INITIAL_SPAWN_RATE
        self.next_update_time = self.get_run_time() + self.get_random_interval(config)

    def get_random_interval(self, config):
        return np.clip(np.random.poisson(config.MEAN_TIME_INTERVAL_SECONDS), 
                       config.MIN_TIME_INTERVAL_SECONDS, 
                       config.MAX_TIME_INTERVAL_SECONDS)

    def tick(self, config=Config):
        """
        Locust calls tick() approximately every second, and user count and spawn rate is adjusted if run time of locust test exceeds the next update time.
        """
        current_run_time = self.get_run_time()

        if current_run_time >= self.next_update_time:
            self.user_count = np.clip(np.random.poisson(config.MEAN_USER_COUNT), 
                                      config.MIN_USER_COUNT, 
                                      config.MAX_USER_COUNT)
            self.spawn_rate = np.clip(np.random.poisson(config.MEAN_SPAWN_RATE), 
                                      config.MIN_SPAWN_RATE, 
                                      config.MAX_SPAWN_RATE)
            self.next_update_time = current_run_time + self.get_random_interval(config)
            print("Next update time at {}s timestep".format(self.next_update_time))

        return self.user_count, self.spawn_rate

class EnvironmentVariables:
    APPLICATION_API_KEY = 'APPLICATION_API_KEY'
    OTHER_API_KEYS = 'OTHER_API_KEYS'

@events.test_start.add_listener
def on_locust_test_start(environment, env_vars=EnvironmentVariables, **kwargs):
    """
    on_locust_init is called when the load test starts.
    """
    attrs = {k: v for k, v in env_vars.__dict__.items() if not k.startswith('__')}
    missing_keys = []

    for k, v in attrs.items():
        setattr(environment, k.lower(), os.environ.get(v))
        if not getattr(environment, k.lower()):
            missing_keys.append(v)

    if missing_keys:
        print(f"{', '.join(missing_keys)} environment variable(s) is/are not set.")
    
    environment.shape = AutoLoadTestShape()
