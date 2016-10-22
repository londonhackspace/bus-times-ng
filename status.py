#!/usr/bin/env python

import json, os, sys, inspect, urllib, datetime
import dateutil.parser
from dateutil import tz

# https://api.tfl.gov.uk/line/mode/tube,overground,dlr,tflrail/status

# the bus stop outside the space is
#
# naptan:AtcoCode 	490011243E
# going East
# ref 48630 (?)
#
# and west bound is:
#
# naptan:AtcoCode 	490011243W
# going West
# ref 76309

# times are in UTC!

class TFL_API:
  def __init__(self, app_id, app_key):
    self.id = app_id
    self.key = app_key

  def auth(self):
    if self.id:
      return "?app_id=%s&app_key=%s" % (self.id, self.key)
    else:
      return ""

  def nicedump(self, thing):
    ks = thing.keys()
    ks.sort()
    for k in ks:
      if not hasattr(thing[k], '__iter__'):
        print k + ": " + str(thing[k])

  def rail_status(self):
    response = urllib.urlopen("https://api.tfl.gov.uk/line/mode/tube,overground,dlr,tflrail/status" + self.auth())
    lines = json.loads(response.read())
    for line in lines:
      print "%20s : %s %d" % (line['name'], line['lineStatuses'][0]['statusSeverityDescription'], line['lineStatuses'][0]['statusSeverity'])
      if len(line['lineStatuses']) != 1:
        for s in line['lineStatuses'][1:]:
          print s['statusSeverityDescription'], s['statusSeverity']
    
  def busstop(self, stopid):
    url = "https://api.tfl.gov.uk/StopPoint/" + stopid + self.auth()
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    name = data["commonName"]
    status = data["status"]
    letter = None
    towards = None
    direction = None
    for c in data["children"]:
      if c["naptanId"] == stopid:
        letter = c["stopLetter"]
        for ap in c["additionalProperties"]:
          if ap["key"] == "Towards":
            towards = ap["value"]
          if ap["key"] == "CompassPoint":
            ds = {'W' : "West", 'E': "East", 'N': "North", 'S': "South"}
            d = ap["value"]
            if d in ds:
              direction = ds[d]
            else:
              direction = d
    if not status:
      self.nicedump(data)
    if letter and towards:
      return "%s (%s), to:\n  %s (%s)" % (name, letter, towards, direction)
    else:
      return "%s" % (name)

  def bus_arrivals(self, stopid):
    url = "https://api.tfl.gov.uk/StopPoint/" + stopid + "/arrivals" + self.auth()
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    data = sorted(data, key=lambda bus: bus["timeToStation"])

    ret = []

    for bus in data:
      # 2016-10-21T18:55:51.3721765Z
      time = dateutil.parser.parse(bus["expectedArrival"])
      time = time.astimezone(tz.tzlocal())
      time = time.strftime('%H:%M:%S')

#      print "%4s to %20s : %s" % (bus["lineName"], bus["destinationName"], time)
      line = bus["lineName"]
      if line == "London Overground":
        line = "Overground"
      dest = bus["destinationName"]
      if dest.endswith(" Rail Station"):
        dest = dest[:dest.find(" Rail Station")]
      ret.append((line, dest, time))

    return ret

if __name__ == "__main__":

  if len(sys.argv) == 3:
    api = TFL_API(sys.argv[1], sys.argv[2])
  else:
    api = TFL_API(None, None)

  api.rail_status()
  print

  def printit(ts):
    ls = [0,0,0]
    for t in ts:
      for i,v in enumerate(t):
        if ls[i] < len(v):
          ls[i] = len(v)
    fmt = "%%%ds %%%ds %%%ds" % (ls[0], ls[1], ls[2])
    for t in ts:
      print fmt % t

  print api.busstop("490011243E")
  a = api.bus_arrivals("490011243E")
  printit(a)
  print

  print api.busstop("490011243W")
  a = api.bus_arrivals("490011243W")
  printit(a)
  print

  # cambridge heath
  print api.busstop("910GCAMHTH")
  a = api.bus_arrivals("910GCAMHTH")
  printit(a)
  print
  
