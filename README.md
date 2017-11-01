# PerformanceTrack
Simple Python script for tracking CPU and memory usage at a system level and as well as individual processes. PerformanceTrack is designed to be triggered via a bash/batch script using a task scheduler like cron or at so that performance data is constantly tracked in the background.

## Installation

**Dependancies**
- [psutil](https://github.com/giampaolo/psutil)

There is no formal installation process but **tracker.py** may need to be modified to run on your system. Also the user must set up a task to run the script files on a regular basis.

**File Paths**

At the top of the script, three filepath variables can be modified to a specific folder if needed. Often a task scheduler will need the full path to these files to be specified in order to control where the files are located.  

```python
DATA_STORE_FILE = 'data.pik' # Add folder path for data pickle
SYSTEM_DATA_EXTRACT_FILE = 'system_log.csv' # Add folder path for system data CSV extract
PROCESS_DATA_EXTRACT_FILE = 'process_log.csv' # Add folder path for process data CSV extract
```

**Process Filter**

PerformanceTracker will log data related to specific processes but uses to filter to avoid logging ALL processes. By adding/removing from the list below, you can modify which types of processes are logged. Processes are filter by reviewing the process name and identifying if the process name **contains** one of the strings in the list.

```python
# Process specific stats name filter
PROCESS_FILTER = ['java', 'python']
```

**CPU Time**

The CPU percentage calculations are determined by monitoring the system/processes for a set period of time. You can modify the amount of time for this calculation by setting the value below.

```python
# Time for CPU Usage calculations (in seconds)
CPU_CALC_TIME = 1.0
```
## Using PerformanceTracker

**Schedule Task**

After tracker.py has been modified, you need to setup a [cron](http://www.unixgeeks.org/security/newbie/unix/cron-1.html) or [at](https://technet.microsoft.com/en-us/library/bb726974.aspx) task (or whatever scheduler you like) to trigger running of the script at a regular interval. Bash/Batch scripts are provided to make this task easier, make sure your task runs **log_current_state_linux.sh** or **log_current_state_windows.cmd** depending on your OS.

If you look at these run scripts they only contain one command which involves two arguments as seen below.

```
python tracker.py [log\extract] [linux\windows]
```

**Generating CSV Extract**

Each time **tracker.py** is triggered, performance data is stored in a pickle instead of written directly to a CSV file. This is done to allow the process to run more quickly and consume less resources. In order to review the data you must generate the CSV files from data stored in the pickle. This can be accomplished by running the **generate_extract_linux.sh** or **generate_extract_windows.cmd** scripts depending on your OS.
