#!/usr/bin/python3

# reads all .toml files (nodes) under ./data/
# and writes a CCMap layer JSON to stdout

import toml
import os
from sys import stderr
import time
import json
from math import sqrt
from os import environ
from common import *

data = get_data()

optional_fields = 'description location inaccuratelocation switch station advisory aliases type filepath'.split(' ')

def format_node(node):
    o = {}
    o['id'] = 'ccmap:kani/node/' + node['name']
    o['name'] = node['name'].title() + ' (KANI)'
    o['x'] = int(node['x'])
    o['z'] = int(node['z'])
    if 'y' in node:
        o['y'] = int(node['y'])
    for key in optional_fields:
        if key in node:
            o[key] = node[key]

    bad_links = ""
    for canon, bad in node['BadLinks'].items():
        bad_links += f"{canon}: {bad}, "
    bad_links.rstrip(", ")
    if bad_links != "":
        o['BadLinks'] = bad_links

    return o

def format_link(node, neighbor):
    n_from, n_to = sorted((node, neighbor),
        key = lambda node: node['name'])
    from_name, to_name = n_from['name'], n_to['name']
    xa, xb = int(n_from['x']), int(n_to['x'])
    za, zb = int(n_from['z']), int(n_to['z'])
    o = {}
    o['type'] = 'link'
    o['id'] = f'ccmap:kani/link/{from_name}/{to_name}'
    o['name'] = f'{from_name.title()} - {to_name.title()} (KANI)'
    o['line'] = [[[ xa, za ], [ xb, zb ]]]
    o['distance'] = int(sqrt((xa-xb)**2 + (za-zb)**2))
    return o

nodes = []
links = {}

for node in data.values():
    nodes.append(format_node(node))
    for neighbor_name in node['links']:
        if neighbor_name == node['name']: continue
        link_id = tuple(sorted((neighbor_name, node['name'])))
        if link_id in links: continue
        neighbor = data[neighbor_name]
        links[link_id] = format_link(node, neighbor)

presentations = [
    {
        "name": "Rails and Stops (KANI)",
        "style_base": {
            "color": "#ff8800",
        },
        "zoom_styles": {
            "-6": { "name": None },
            "-2": { "name": "$name" },
        },
    },
]

collection = {
    "name": "Rails",
    "info": {
        "version": "3.0.0-beta3",
    },
    "presentations": presentations,
    "features":
        list(sorted(nodes,
            key = lambda node: node['id']))
        + list(sorted(links.values(),
            key = lambda link: link['id'])),
}

collection_string = json.dumps(collection, indent = None, separators = (',', ':'), sort_keys = True)
# apply line breaks for readability and nice diffs
collection_string = collection_string.replace("},{", "},\n{")
print(collection_string)
