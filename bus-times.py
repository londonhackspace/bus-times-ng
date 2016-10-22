#!/usr/bin/env python

import curses, sys
from status import TFL_API
from time import sleep

win = curses.initscr()
curses.start_color()

curses.init_pair(1, curses.COLOR_WHITE,  curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_RED,    curses.COLOR_BLACK)

win.clear();
win.addstr( 4, 4, "Fetching data..." );
win.refresh();

if len(sys.argv) == 3:
  api = TFL_API(sys.argv[1], sys.argv[2])
else:
  api = TFL_API(None, None)

stops = ("490011243E", "490011243W", "910GCAMHTH")

while True:
  for stop in stops:
    win.clear()
    try:
      name = api.busstop(stop)
      win.addstr(1,2, "Departures for:")
      win.addstr(2,2, name)
      arrivals = api.bus_arrivals(stop)
    except (ValueError, IOError):
      win.attron(curses.A_BOLD)
      win.attron(curses.color_pair(3))
      win.addstr(1, 2, "Network failure / offline")
      win.attroff(curses.color_pair(3))
      win.attroff(curses.A_BOLD)
      win.refresh()
      sleep(10)
      continue
      
    win.attron(curses.A_BOLD)

    ls = [0,0,0]
    for a in arrivals:
      for i,v in enumerate(a):
        if ls[i] < len(v):
          ls[i] = len(v)
    fmt = "%%%ds  %%%ds  %%%ds" % (ls[0], ls[1], ls[2])
    
    for i,a in enumerate(arrivals):
      col = (i % 2) + 1
      win.attron(curses.color_pair(col))
      win.addstr(5 + i, 5, fmt % a)
      win.attroff(curses.color_pair(col))
    
    win.attroff(curses.A_BOLD)
    win.refresh()
    sleep(10)

curses.endwin()
