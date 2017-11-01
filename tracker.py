import csv
import datetime
import pickle
import psutil
import os
import sys


# Locations for storage and export files
DATA_STORE_FILE = 'C:/ross/repository/PerformanceTrack/data.pik' # Insert file path for data pickle
SYSTEM_DATA_EXTRACT_FILE = 'C:/ross/repository/PerformanceTrack/system_log.csv' # Insert file path for system data CSV extract
PROCESS_DATA_EXTRACT_FILE = 'C:/ross/repository/PerformanceTrack/process_log.csv' # Insert file path for process data CSV extract

# Process specific stats name filter
PROCESS_FILTER = ['java', 'python']

# Time for CPU Usage calculations (in seconds)
CPU_CALC_TIME = 1.0


# Log performance for system and process level metrics and store
def log_current_state(os_type):

    time = datetime.datetime.now()

    new_system_data = system_performance_metrics(time)
    new_processes_data = process_performance_metrics(time, os_type)
    store(new_system_data, new_processes_data)


# Analyze performance of system level metrics
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


# Analyze performance of filtered processes
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
        data = {'system': [], 'processes': []}
    else:
        data = pickle.load(open(DATA_STORE_FILE, 'rb'))

    data['system'].append(new_system_data)
    data['processes'].extend(new_processes_data)

    pickle.dump(data, open(DATA_STORE_FILE, 'wb'))


# Generate CSV files from data pickle
def generate_extract():

    data = pickle.load(open(DATA_STORE_FILE, 'rb'))

    system_data = data['system']
    process_data = data['processes']

    system_data_headers = ['cpu_usage', 'datetime', 'mem_available', 'mem_percent_used', 'mem_total', 'mem_used']
    write_csv(system_data, system_data_headers, SYSTEM_DATA_EXTRACT_FILE)

    process_data_headers = ['cpu_usage', 'datetime', 'filter', 'name', 'pid', 'rss_memory', 'vms_memory']
    write_csv(process_data, process_data_headers, PROCESS_DATA_EXTRACT_FILE)


# Write CSV file from a list of dictionaries
def write_csv(data, headers, file_location):

    csv_file = open(file_location, 'w+', newline='')
    writer = csv.DictWriter(csv_file, headers)

    writer.writeheader()
    writer.writerows(data)


if __name__ == '__main__':

    os_type = sys.argv[2]

    if sys.argv[1] == 'log':
        log_current_state(os_type)
    elif sys.argv[1] == 'extract':
        generate_extract()
