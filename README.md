Certainly! Here's a simple README.md file for your `caltime.py` project:

---

# Caltime - Caldav Time Tracker

## Overview

`caltime.py` is a command-line program that allows users to track time spent on projects using an ICS calendar file. It utilizes the CalDAV protocol to interact with a calendar server.

## Features

- Record time spent on activities with a simple timer.
- Save recorded activities to a specified calendar in ICS format.
- List recorded activities, showing dates, event names, and hours spent.
- View monthly summaries of time spent on activities.

## Requirements

- Python 3
- [PrettyTable](https://pypi.org/project/prettytable/)
- [python-caldav](https://python-caldav.readthedocs.io/en/latest/)
- [humanize](https://pypi.org/project/humanize/)

## Installation

1. Install required dependencies:

   ```bash
   pip install prettytable python-caldav humanize
   ```

2. Set up your CalDAV server and configure access in the `secrets.py` file.

   ```python
   # secrets.py
   url = "your_caldav_server_url"
   username = "your_username"
   password = "your_password"
   ```

3. Run `caltime.py` using the provided commands.

## Usage

### Record Time

To start recording time for an activity:

```bash
./caltime.py record <activity_name> -C <calendar_name> -B <begin_time>
```

- `<activity_name>`: Name of the activity.
- `-C <calendar_name>`: (Optional) Specify the calendar to save the activity. Default is "Caltime".
- `-B <begin_time>`: (Optional) Specify the start time for the activity. Default is the current time.

### List Activities

To list recorded activities:

```bash
./caltime.py list -C <calendar_name> -M
```

- `-C <calendar_name>`: (Optional) Specify the calendar to list activities. Default is "Caltime".
- `-M`: (Optional) Show monthly summaries.

## Examples

```bash
# Record time for a project
./caltime.py record "Project A" -C "Work" -B "2024-01-25T09:00:00"

# List all recorded activities
./caltime.py list

# List monthly summaries
./caltime.py list -M
```
