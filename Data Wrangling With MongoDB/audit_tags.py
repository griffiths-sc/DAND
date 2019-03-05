#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
import pprint
import sys

def count_elem_tags(elem,tag_type=None,tags={}):
    # Function to return count of top level element if tag_type is None,
    # else count of specified tag (ignores unknown tags)
    if tag_type==None:
        if elem.tag in tags:
            tags[elem.tag]+=1
        else:
            tags[elem.tag]=1
    else:
        if elem.tag==tag_type:
            for child in elem.getchildren():
                if child.tag=='tag':
                    k=child.get('k')
                    if k in tags:
                        tags[k]+=1
                    else:
                        tags[k]=1
    return tags

def count_tags(filename):
    # Count all tags in file
    tags={}
    node_tags={}
    way_tags={}
    for event,elem in ET.iterparse(filename):
        tags=count_elem_tags(elem,tag_type=None,tags=tags)
        node_tags=count_elem_tags(elem,tag_type='node',tags=node_tags)
        way_tags=count_elem_tags(elem,tag_type='way',tags=way_tags)
    return tags,node_tags,way_tags

def audit_tags(filename):
    # Print count of top-level, node and way tags
    tags,node_tags,way_tags=count_tags(filename)
    print('\nTOP LEVEL ELEMENTS:\n')
    pprint.pprint(tags,indent=2)
    print('\nNODE TAGS:\n')
    pprint.pprint(node_tags,indent=2)
    print('\nWAY TAGS:\n')
    pprint.pprint(way_tags,indent=2)


if __name__ == "__main__":
    filename=sys.argv[1]
    audit_tags(filename)
