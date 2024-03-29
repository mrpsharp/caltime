#!/Users/petersharp/miniconda3/envs/caltime/bin/python
## caltime.py - a caldav time tracker

## Settings are saved in secrets.py which is ignored by git.

# secrets.py
# url = ""
# username = ""
# password = ""

import secrets

import argparse
import humanize
import datetime as dt
import time
import readchar
import caldav

from prettytable import PrettyTable
from dateutil.parser import parse

def timer(args, begin = dt.datetime.now()):
    msg = ""
    if args.begin:
        begin = parse(args.begin, fuzzy=True)
    try: 
        while True:
            delta = dt.datetime.now() - begin
            print(" " * len(msg), end="\r", flush=True) # clear the printed line
            msg = "You started "+args.activity+" "+humanize.naturaltime(delta)
            print(msg, end='\r')
            time.sleep(1)
    except KeyboardInterrupt:
        print("  ", end="\r", flush=True)
        msg = "Ctrl-c was pressed. Do you really want to end and save activity? (Y)es, (N)o, e(X)it "
        print(msg, end="", flush=True)
        res = readchar.readchar()
        if res == 'Y' or res == 'y':
            end = dt.datetime.now()
            print("\nYou spent " + humanize.precisedelta(end - begin, minimum_unit="seconds")+" on "+args.activity)
            save_cal(args,begin,end)
            exit(1)
        elif res == 'X' or res=='x':
            end = dt.datetime.now()
            print("\nYou spent " + humanize.precisedelta(end - begin, minimum_unit="seconds")+" on "+args.activity)
            print("Activity was not saved")
            exit(1)
        else:
            print("  ", end="\r", flush=True)
            print(" " * len(msg), end="", flush=True) # clear the printed line
            print("    ", end="\r", flush=True)
            timer(args,begin)

def save_cal(args,begin,end):
    calendar = open_cal(args)
    event = calendar.save_event(
        dtstart = begin,
        dtend = end,
        summary=args.activity,
        description="Created with caltime"
        )
    print(args.activity,"was added to calendar", calendar.name)
    
def open_cal(args):
    if args.calendar:
        calendar = args.calendar
        print("Using calendar", calendar)
    else:
        calendar = "Caltime"
        print("No calendar specificed, using", calendar)
    with caldav.DAVClient(url=secrets.url, username=secrets.username, password=secrets.password) as client:
        dav_principal = client.principal()
    try:
        dav_calendar = dav_principal.calendar(name=calendar)
    except caldav.error.NotFoundError:
        if calendar=="Caltime":
            dav_calendar = dav_principal.make_calendar(name="Caltime")
            print("Caltime calendar created")
        else:
            print("Calendar",calendar,"not found, using Caltime")
    return dav_calendar

def list(args):
    calendar = open_cal(args)
    calevents = calendar.search(event=True)
    events = []
    for event in calevents:
        try:
            events.append({
                "start": event.icalendar_component.get("dtstart").dt,
                "end": event.icalendar_component.get("dtend").dt,
                "summary": event.icalendar_component.get("summary")
            })
        except:
            print("Error when reading event:")
            print(event.data)
            exit(1)
    events = sorted(events, key=lambda d: d['start'])
    if args.month:
        month_times = []
        current_month = ""
        for event in events:
            begin = event['start']
            end = event['end']
            t_delta = end - begin
            t_delta_float = float(t_delta.total_seconds())/3600
            month = begin.strftime('%B %Y')
            if month == current_month:
                month_times[-1]['total'] += t_delta_float
            else:
                current_month = month
                new_month = {
                    "month":current_month,
                    "total":t_delta_float} 
                month_times.append(new_month)
        output = PrettyTable()
        output.field_names=["Month", "Hours"]
        output.align = "l"
        for month in month_times:
            output.add_row([month["month"], "{:0.1f}".format(month["total"])])
        print(output)
    else:
        output = PrettyTable()
        output.field_names=["Date", "Event", "Hours"]
        output.align = "l"
        total_hours = 0
        for event in events:
            begin = event['start']
            end = event['end']
            summary = event['summary']
            t_delta = end - begin
            t_delta_float = float(t_delta.total_seconds())/3600
            total_hours += t_delta_float
            output.add_row(["  {:%d/%m/%y}".format(begin),summary, "{:.1f}".format(t_delta_float)])
        output.add_row(["","TOTAL" ,"{:0.1f}".format(total_hours)], divider=True)
        print(output)

def build_parser():
    parser=argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    # timer
    parser_timer = subparsers.add_parser('record')
    parser_timer.add_argument('activity', type=str)
    parser_timer.add_argument('-C', '--calendar', type=str)
    parser_timer.add_argument('-B', '--begin', type=str)
    parser_timer.set_defaults(func=timer)

    # list
    parser_list = subparsers.add_parser('list')
    parser_list.add_argument('-C', '--calendar', type=str)
    parser_list.add_argument('-M', '--month', action='store_true')
    parser_list.set_defaults(func=list)
    return parser

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
