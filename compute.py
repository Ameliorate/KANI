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

class Node:
    def __init__(self, parent=None,  canonical_destination=None):
        self.parent = parent
        self.canonical_destination = canonical_destination
        self.data = data[canonical_destination]
        self.position = (self.data.get('x') or 0, self.data.get('z') or 0)

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __repr__(self):
        return f"{self.position} {self.canonical_destination}- g: {self.g} h: {self.h} f: {self.f}"

def route(from_canon, to_canon):
    print(f"Routing from {from_canon} to {to_canon}", file=stderr)
    from_data = data[from_canon]
    to_data = data[to_canon]
    open_list = deque([Node(None, from_canon)])
    closed_list = deque([])
    while len(open_list):
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index
        del open_list[current_index]
        closed_list.append(current_node)
        
        if current_node.canonical_destination == to_canon:
            dest = []
            current = current_node
            while current is not None:
                canon_dest = current.canonical_destination
                if current.parent is not None:
                    canon_dest = current.parent.data['BadLinks'].get(current.canonical_destination) or current.canonical_destination
                dest.append(canon_dest)
                current = current.parent
            return ' '.join(dest[::-1])
        links = deque([])
        for link in current_node.data['links']:
            new_node = Node(current_node, link)
            links.append(new_node)
        for link in links:
            isRoutable = link.data.get('station') or link.data.get('switch') or False
            if not isRoutable and not link.canonical_destination == to_canon and not link.canonical_destination == from_canon:
                continue
            if len([closed_child for closed_child in closed_list if closed_child == link]) > 0:
                continue
            link.g = current_node.g + 1
            link.h = ((link.position[0] - to_data['x']) ** 2) + ((link.position[1] - to_data['z']) ** 2)
            link.f = link.g + link.h
            if len([open_node for open_node in open_list if link.canonical_destination == open_node.canonical_destination and link.g > open_node.g]) > 0:
                continue
            open_list.append(link)

routeData = []

for from_canon in data.keys():
    for to_canon in data.keys():
        myRoute = route(from_canon, to_canon)
        if myRoute is None:
            exit(f"Can't route between {from_canon} and {to_canon}! Is the station connected to nexus?")
        if data[to_canon].get('station'):
            myRoute = myRoute + f" {to_canon}:exit"
        routeData.append({'dest': myRoute, 'from': from_canon, 'to': to_canon})

jsonRouteData = json.dumps(routeData)
print(jsonRouteData)
