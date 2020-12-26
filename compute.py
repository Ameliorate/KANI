#!/usr/bin/python3

import toml
import os
from sys import stderr
from collections import deque
from copy import deepcopy
import json

datadir = r'./data'

data = {}

def processFile(path, name):
    print(f"Processing file {path}", file=stderr)
    name = name.removesuffix('.toml')
    myData = toml.load(path)
    if 'links' not in myData:
        myData['links'] = []
    if 'BadLinks' not in myData:
        myData['BadLinks'] = {}
    data[name] = myData

for subdir, dirs, files in os.walk(datadir):
    for filename in files:
        filepath = subdir + os.sep + filename

        if filepath.endswith('.toml'):
            processFile(filepath, filename)


def route(from_canon, to_canon):
    # TODO: Use the x and z properties to generate a hurestic and score that minimizes distance traveled, using A*
    myData = data[from_canon]
    dist = {from_canon: (myData['BadLinks'].get(from_canon) or from_canon)}
    q = deque([from_canon])
    while len(q):
        at = q.popleft()
        myData = data[at]
        for next in myData['links']:
            if next not in dist:
                dist[next] = dist[at] + ' ' + (myData['BadLinks'].get(next) or next)
                q.append(next)
    return dist.get(to_canon)

routeData = []

for from_canon in data.keys():
    for to_canon in data.keys():
        myRoute = route(from_canon, to_canon)
        if myRoute is None:
            print(routeData)
            exit(f"Can't route between {from_canon} and {to_canon}! Is the station connected to nexus?")
        routeData.append({'dest': myRoute, 'from': from_canon, 'to': to_canon})

jsonRouteData = json.dumps(routeData)
print(jsonRouteData)

