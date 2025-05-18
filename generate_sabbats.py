#!/usr/bin/env python3

import datetime
from skyfield import api, almanac
from icalendar import Calendar, Event

# Compute solstices, equinoxes, and cross-quarter midpoints for a given year
def compute_events_for_year(year, eph):
    ts = api.load.timescale()
    t0 = ts.utc(year, 1, 1)
    t1 = ts.utc(year, 12, 31, 23, 59, 59)
    times, events = almanac.find_discrete(t0, t1, almanac.seasons(eph))

    # Map Skyfield’s numeric codes to your sabbat names
    labels = {
        0: 'Ostara (Spring Equinox)',
        1: 'Litha (Summer Solstice)',
        2: 'Mabon (Autumn Equinox)',
        3: 'Yule (Winter Solstice)',
    }
    quarters = [
        (times[i].utc_datetime(), labels[event])
        for i, event in enumerate(events)
        if event in labels
    ]

    # Cross-quarter names by pairing adjacent quarter days
    names = {
        ('Yule',   'Ostara'):  'Imbolc',
        ('Ostara', 'Litha'):   'Beltane',
        ('Litha',  'Mabon'):   'Lughnasadh',
        ('Mabon',  'Yule'):    'Samhain',
    }
    crosses = []
    for (d1, t1), (d2, t2) in zip(quarters, quarters[1:] + [quarters[0]]):
        mid = d1 + (d2 - d1) / 2
        key = (t1.split()[0], t2.split()[0])
        crosses.append((mid, names[key]))

    return quarters + crosses

# Main entry point: generate this year’s sabbats only
def main(output_path='wiccan-sabbats.ics'):
    year = datetime.date.today().year
    eph = api.load('de421.bsp')

    cal = Calendar()
    cal.add('prodid', '-//Wiccan Sabbats Calendar//')
    cal.add('version', '2.0')
    cal.add('X-PUBLISHED-TTL', 'P1D')  # advise clients to refresh daily

    # Generate exactly this year’s eight sabbats
    for dt, title in compute_events_for_year(year, eph):
        ev = Event()
        # Unique ID ensures updates replace prior entries
        uid = f"{title}-{dt.date().isoformat()}@wiccan-sabbats"
        ev.add('uid', uid)
        ev.add('summary', title)
        ev.add('dtstart', dt.date())
        ev.add('dtstamp', datetime.datetime.utcnow())
        cal.add_component(ev)

    # Write the .ics file
    with open(output_path, 'wb') as f:
        f.write(cal.to_ical())
    print(f"Created {output_path} for year {year}")

if __name__ == '__main__':
    main()
