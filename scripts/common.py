import toml
import os
from sys import stderr

datadir = r'./data'

def process_file(path, name):
    try:
        name = name.removesuffix('.toml')
        myData = toml.load(path)
        myData['name'] = name
        myData['filepath'] = path
        myData['type'] = path.split(os.sep)[2]
        if 'BadLinks' not in myData:
            myData['BadLinks'] = {}
        return myData
    except Exception as e:
        print(f"Error while reading file {path}", file=stderr)
        raise e

def get_data():
    data = {}
    for subdir, dirs, files in os.walk(datadir):
        for filename in files:
            filepath = subdir + os.sep + filename

            if filepath.endswith('.toml'):
                data[filename.removesuffix('.toml')] = process_file(filepath, filename)
    return data
