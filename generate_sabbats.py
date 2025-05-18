#!/usr/bin/env python3
import datetime
from skyfield import api, almanac
from icalendar import Calendar, Event

def compute_quarter_events(year, eph):
    ts = api.load.timescale()
    t0 = ts.utc(year, 1, 1)
    t1 = ts.utc(year, 12, 31, 23, 59, 59)
    times, events = almanac.find_discrete(t0, t1, almanac.seasons(eph))
    labels = {
        0: 'Ostara (Spring Equinox)',
        1: 'Litha (Summer Solstice)',
        2: 'Mabon (Autumn Equinox)',
        3: 'Yule (Winter Solstice)',
    }
    return [(times[i].utc_datetime().date(), labels[event])
            for i, event in enumerate(events)
            if event in labels]

def main(output_path='wiccan-sabbats.ics'):
    year = datetime.date.today().year
    eph = api.load('de421.bsp')
    cal = Calendar()
    cal.add('prodid', '-//Wiccan Sabbats Calendar//')
    cal.add('version', '2.0')
    cal.add('X-PUBLISHED-TTL', 'P1D')
    quarters = compute_quarter_events(year, eph)
    crosses = [
        (datetime.date(year, 2, 1), 'Imbolc'),
        (datetime.date(year, 5, 1), 'Beltane'),
        (datetime.date(year, 8, 1), 'Lughnasadh'),
        (datetime.date(year, 10, 31), 'Samhain'),
    ]
    all_sabbats = sorted(quarters + crosses, key=lambda x: x[0])
    for date, title in all_sabbats:
        ev = Event()
        ev.add('uid', f"{title}-{date.isoformat()}@wiccan-sabbats")
        ev.add('summary', title)
        ev.add('dtstart', date)
        ev.add('dtstamp', datetime.datetime.utcnow())
        cal.add_component(ev)
    with open(output_path, 'wb') as f:
        f.write(cal.to_ical())
    print(f"Created {output_path} for year {year}")

if __name__ == '__main__':
    main()
