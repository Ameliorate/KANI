#!/usr/bin/python3

import json
from common import *

data = get_data()
exported = json.dumps(data, indent="\t", sort_keys=True)
print(exported)
