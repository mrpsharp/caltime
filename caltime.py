import argparse
import humanize
import datetime as dt
import time
import readchar
import caldav
import secrets
from prettytable import PrettyTable

def timer(args, start = dt.datetime.now()):
    msg = ""
    if args.start:
        hour = int(args.start.split(":")[0])
        minute = int(args.start.split(":")[1])
        start = dt.datetime.now().replace(hour=hour, minute=minute)
    try: 
        while True:
            delta = dt.datetime.now() - start
            print(" " * len(msg), end="\r", flush=True) # clear the printed line
            msg = "You started "+args.activity+" "+humanize.naturaltime(delta)
            print(msg, end='\r')
            time.sleep(1)
    except KeyboardInterrupt:
        print("  ", end="\r", flush=True)
        msg = "Ctrl-c was pressed. Do you really want to stop and save activity? (Y)es, (N)o, e(X)it "
        print(msg, end="", flush=True)
        res = readchar.readchar()
        if res == 'Y' or res == 'y':
            stop = dt.datetime.now()
            print("\nYou spent " + humanize.precisedelta(stop - start, minimum_unit="seconds")+" on "+args.activity)
            save_cal(args,start,stop)
            exit(1)
        elif res == 'X' or res=='x':
            stop = dt.datetime.now()
            print("\nYou spent " + humanize.precisedelta(stop - start, minimum_unit="seconds")+" on "+args.activity)
            print("Activity was not saved")
            exit(1)
        else:
            print("  ", end="\r", flush=True)
            print(" " * len(msg), end="", flush=True) # clear the printed line
            print("    ", end="\r", flush=True)
            timer(args,start)

def save_cal(args,start,stop):
    dalendar = open_cal(args)
    event = calendar.save_event(
        dtstart = start,
        dtend = stop,
        summary=args.activity,
        description="Created with caltime"
        )
    print(args.activity,"was added to calendar", calendar.name)
    
def open_cal(args):
    if args.calendar:
        calendar = args.calendar
    else:
        calendar = "Caltime"
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
        events.append({
            "start": event.icalendar_component.get("dtstart").dt,
            "end": event.icalendar_component.get("dtend").dt,
            "summary": event.icalendar_component.get("summary")
        })
    events = sorted(events, key=lambda d: d['start'])
    if args.month:
        print("Monthly")
    else:
        output = PrettyTable()
        output.field_names=["Date", "Event", "Hours"]
        output.align = "l"
        total_hours = 0
        for event in events:
            start = event['start']
            end = event['end']
            summary = event['summary']
            t_delta = end - start
            t_delta_float = float(t_delta.total_seconds())/3600
            total_hours += t_delta_float
            output.add_row(["  {:%d/%m/%y}".format(start),summary, "{:.1f}".format(t_delta_float)])
        output.add_row(["","TOTAL" ,"{:0.1f}".format(total_hours)], divider=True)
        print(output)


parser=argparse.ArgumentParser()
subparsers = parser.add_subparsers(required=True)

# timer
parser_timer = subparsers.add_parser('start')
parser_timer.add_argument('activity', type=str)
parser_timer.add_argument('-C', '--calendar', type=str)
parser_timer.add_argument('-S', '--start', type=str)
parser_timer.set_defaults(func=timer)

# list
parser_list = subparsers.add_parser('list')
parser_list.add_argument('-C', '--calendar', type=str)
parser_list.add_argument('-M', '--month', action='store_true')
parser_list.set_defaults(func=list)

args = parser.parse_args()
args.func(args)