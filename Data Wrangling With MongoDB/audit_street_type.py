#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import sys

# Regular expression
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

# Expected street types
expected = ["Close", "Crescent", "Green", "Grove", "Park", "Rise", "View", "Walk", "Way",
            "Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
            
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit_street_types(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


if __name__ == "__main__":
    filename=sys.argv[1]
    st_types = audit_street_types(filename)
    pprint.pprint(dict(st_types))
