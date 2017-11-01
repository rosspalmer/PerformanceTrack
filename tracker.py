import datetime
import pandas as pd
import pickle
import psutil
import os
import sys

import time


# Locations for storage and export files
DATA_STORE_FILE = # Insert file path for data pickle
SYSTEM_DATA_EXTRACT_FILE = # Insert file path for system data CSV extract
PROCESS_DATA_EXTRACT_FILE = # Insert file path for process data CSV extract

# Process specific stats name filter
PROCESS_FILTER = ['java', 'python']

# Time for CPU Usage calculations (in seconds)
CPU_CALC_TIME = 1.0

def log_current_state(os_type):

    time = datetime.datetime.now()

    new_system_data = system_performance_metrics(time)
    new_processes_data = process_performance_metrics(time, os_type)
    store(new_system_data, new_processes_data)


def system_performance_metrics(time):

    # Setup entry dictionary and log time
    entry = {}
    entry['datetime'] = time

    # Log CPU statistics
    entry['cpu_usage'] = psutil.cpu_percent(CPU_CALC_TIME)

    # Log memory statistics
    mem = psutil.virtual_memory()
    entry['mem_total'] = mem.total
    entry['mem_available'] = mem.available
    entry['mem_used'] = mem.used
    entry['mem_percent_used'] = entry['mem_used'] / entry['mem_total']

    return entry


def process_performance_metrics(time, os_type):

    filtered_processes = []

    memory_label = None
    if os_type == 'windows':
        memory_label = 'memory_info'
    elif os_type == 'linux':
        memory_label = 'memory_full_info'

    # Loop through process data
    for process in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', memory_label]):
        for process_filter_string in PROCESS_FILTER:
            if process_filter_string in process.info['name']:
                entry = {}
                entry['datetime'] = time
                entry['filter'] = process_filter_string
                entry['name'] = process.info['name']
                entry['pid'] = process.info['pid']
                entry['cpu_usage'] = process.cpu_percent(CPU_CALC_TIME)
                entry['rss_memory'] = process.info[memory_label].rss
                entry['vms_memory'] = process.info[memory_label].vms
                filtered_processes.append(entry)

    return filtered_processes

# Store new metrics in data pickle
def store(new_system_data, new_processes_data):

    if not os.path.isfile(DATA_STORE_FILE):
        data = {'system':[], 'processes':[]}
    else:
        data = pickle.load(open(DATA_STORE_FILE, 'rb'))

    data['system'].append(new_system_data)
    data['processes'].extend(new_processes_data)

    pickle.dump(data, open(DATA_STORE_FILE, 'wb'))


def generate_extract():

    data = pickle.load(open(DATA_STORE_FILE, 'rb'))

    system_data = data['system']
    process_data = data['processes']

    system_df = pd.DataFrame(system_data)
    system_df.to_csv(SYSTEM_DATA_EXTRACT_FILE, index=False)

    process_df = pd.DataFrame(process_data)
    process_df.to_csv(PROCESS_DATA_EXTRACT_FILE, index=False)


if __name__ == '__main__':

    os_type = sys.argv[2]

    if sys.argv[1] == 'log':
        log_current_state(os_type)
    elif sys.argv[1] == 'extract':
        generate_extract()
