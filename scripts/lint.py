#!/usr/bin/python3

from dijkstar import Graph, find_path, NoPathError
from common import *

data = get_data()

has_error = False

coordinates = {} # used for coordinate collision check
aliases = {} # used for aliases collision check

# create routing graph for use in checks
graph = Graph()

for destination in data.keys():
    dest_data = data[destination]
    if 'links' in dest_data:
        for link in dest_data['links']:
            graph.add_edge(destination, link, 1)

# start the checking
for destination in data.keys():
    dest_data = data[destination]

    # has an x and z
    if 'x' not in dest_data:
        print(f"{destination} does not have an x coordinate")
        has_error = True
    if 'z' not in dest_data:
        print(f"{destination} does not have a z coordinate")
        has_error = True

    # doesn't share an x and z with any other station
    if 'x' in dest_data and 'z' in dest_data:
        coord = (dest_data['x'], dest_data['z'])
        if coord in coordinates:
            shares = coordinates[coord]
            print(f"{destination} shares coordinate with {shares}")
            has_error = True

        coordinates[coord] = destination

    # lists what it is linked to
    if 'links' not in dest_data:
        print(f"{destination} does not list what stations it is connected to")
        has_error = True

    # check over all links
    for link in dest_data['links']:

        # make sure link exists
        if link not in data:
            print(f"{destination} contains unknown link {link}")
            has_error = True
            continue

        link_data = data[link]

        # if a link is listed, make sure the link lists the destination too
        if destination not in link_data.get('links'):
            print(f"{destination} lists link {link}, however {link} does not list link {destination}")
            has_error = True

    # if is in switches folder, check if switch    
    if dest_data['type'] == "CompliantSwitches" or dest_data['type'] == "NonCompliantSwitches":
        if not dest_data.get('switch') and not dest_data.get('station'):
            print(f"{destination} is in a switch folder but does not have switch or station = true")
            has_error = True

    # lint all aliases
    if 'aliases' in dest_data:
        for alias in dest_data.get('aliases'):

            # check for duplicate aliases
            if alias in aliases:
                otheralias = aliases[alias]
                print(f"{destination} has alias {alias} that also points to {otheralias}")
                has_error = True
            else:
                aliases[alias] = destination

            # check for aliases that are also canonical destination
            for destination2 in data.keys():
                if alias == destination2:
                    print(f"{destination} has alias {alias} that is also a canonical destination")
                    has_error = True

    # check if node is connected to 0,0
    try:
        find_path(graph, destination, "0,0")
    except NoPathError:
        print(f"{destination} is not connected to 0,0")
        has_error = True

if has_error:
    exit(1)
