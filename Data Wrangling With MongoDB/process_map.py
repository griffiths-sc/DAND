#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import schema
import sys

# Output files
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

# Regular expressions
unwanted_re=re.compile(r'[\[\]().\']|(amp;)')
ignore_re=re.compile(r'(^not)|(^todo)|(fixme)',re.IGNORECASE)
suffix_re=re.compile(r'(_\d*$)',re.IGNORECASE)
postcode_re=re.compile(r'\w+\d+\s*\d+\w+',re.IGNORECASE)

# Validation schema
SCHEMA = schema.schema

# CSV fields to match sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

# Keys known to contain multiple values
multival_keys = ['amenity', 'cuisine']

# Acceptable abbreviations
acceptable = ['UK', 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

# Mappings for replacement functions
abbr_mapping = { "Blvd": "Boulevard",
            "By-Pass": "Bypass",
            "Ave": "Avenue",
            "Rd": "Road",
            "Sq": "Square",
            "Ph": "Public House",
            "Cofe": "Church Of England"
            }
welsh_mapping = { " Y ": "-Y-",
            " Yn ": "-Yn-",
            " Yr ": "-Yr-",
            "Y ": "Y-",
            "Yn ": "Yn-",
            "Yr ": "Yr-"
            }
lang_mapping = { "ar": "Arabic",
            "ca": "Catalan, Valencian",
            "cy": "Welsh",
            "de": "German",
            "en": "English",
            "eo": "Esperanto",
            "es": "Spanish, Castilian",
            "et": "Estonian",
            "fa": "Persian",
            "fi": "Finnish",
            "fr": "French",
            "gd": "Gaelic, Scottish Gaelic",
            "gl": "Galician",
            "he": "Hebrew (modern)",
            "hu": "Hungarian",
            "it": "Italian",
            "la": "Latin",
            "lt": "Lithuanian",
            "ru": "Russian",
            "sr": "Serbian",
            "uk": "Ukrainian"
            }

################################################################################
# key cleaning functions
################################################################################

def update_lang(k):
    # Re-order name keys and map to full language name
    for old_str,new_str in lang_mapping.iteritems():
        if k=='name:'+old_str:
            k=new_str+':name'
            break # Found mapping so no need to carry on searching
    return k

def fix_key(k):
    if ignore_re.search(k):
        # Tag not needed
        k=None
    else:
        # Remove suffix
        k=re.sub(suffix_re,'',k)
        if k.startswith('name:'):
            # Update language
            k=update_lang(k)
    return k

################################################################################
# value cleaning functions
################################################################################

def remove_unwanted(v):
    # Remove unwanted characters
    return re.sub(unwanted_re,'',v)

def capitalise(v):
    # Begin each word with a capital letter
    return v.title()

def update_abbr(v):
    # Expand abbreviations
    for old_str,new_str in abbr_mapping.iteritems():
        v_re=re.compile(r'\b'+old_str+r'\b')
        m = v_re.search(v)
        if m:
            v=re.sub(r'\b'+old_str+r'\b',new_str,v)
    return v

def update_welsh(v):
    # Correct hyphenation in Welsh names
    for old_str,new_str in welsh_mapping.iteritems():
        v_re=re.compile(r'\b'+old_str+r'\b')
        m = v_re.search(v)
        if m:
            v=re.sub(r'\b'+old_str+r'\b',new_str,v)
    return v

def ignore_vals(v):
    # Ignore post codes, URLs & acceptable abbreviations
    ignore=False
    if postcode_re.search(v):
        ignore=True
    elif v.startswith('www') or v.startswith('http'):
        ignore=True
    elif v in acceptable:
        ignore=True
    return ignore
        
def fix_vals(v):
    if not ignore_vals(v):
        v=remove_unwanted(v)
        v=capitalise(v)
        v=update_abbr(v)
        v=update_welsh(v)
    return v

################################################################################
# tag formatting function
################################################################################

def format_tag(k,v):
    # Determine key type
    c=k.find(':')
    if c>=0:
        t=k[:c]
        k=k[(c+1):]
    else:
        t='regular'
    return k,v,t

################################################################################
# element processing function
################################################################################

def process_element(element):
    # Clean and shape node or way XML element to Python dict

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []

    # Node and Way elements
    if element.tag == 'node':
        for field in NODE_FIELDS:
            node_attribs[field]=element.get(field)
    elif element.tag == 'way':
        for field in WAY_FIELDS:
            way_attribs[field]=element.get(field)
        pos=0
        for child in element.getchildren():
            if child.tag=='nd':
                way_node={}
                way_node['id']=element.get('id')
                way_node['node_id']=child.get('ref')
                way_node['position']=pos
                pos+=1
                way_nodes.append(way_node)

    # Secondary tags
    for child in element.getchildren():
        if child.tag=='tag':
            tag={}
            k=fix_key(child.get('k'))
            if k!=None:
                c=child.get('v')
                # If value contains multiple entries separated by ';'
                # Duplicate tag for each value
                if k in multival_keys:
                    vals=c.split(';')
                else:
                    vals=[c]
                for v in vals:
                    k,v,t=format_tag(k,v)
                    v=fix_vals(v)
                    tag['id']=element.get('id')
                    tag['key']=k
                    tag['value']=v
                    tag['type']=t
                    tags.append(tag)

    if element.tag == 'node':
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

################################################################################
# Helper functions
################################################################################

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))

class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

################################################################################
# Main function
################################################################################

def process_map(file_in,validate=False,header=False):
    """
    Iteratively process each XML element and write to csv(s)

    file_in:   OSM.xml file to be processed
    validate:  Flag to enable/disable validating the data against the supplied schema
               (Validation is ~ 10X slower)
    header:    Flag to enable/disable writing the header row
               (Headers cause problems when importing data into an existing SQL table)
    """

    with codecs.open(NODES_PATH, 'wb') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'wb') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'wb') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'wb') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'wb') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        if header:
            # Write headers
            nodes_writer.writeheader()
            node_tags_writer.writeheader()
            ways_writer.writeheader()
            way_nodes_writer.writeheader()
            way_tags_writer.writeheader()

        if validate:
            # Instantiate validator
            validator=cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            # Clean the data
            el = process_element(element)
            if el:
                if validate:
                    # Validate
                    validate_element(el, validator)

                # Write to CSV files
                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

if __name__ == "__main__":
    filename=sys.argv[1]
    process_map(filename,validate=False,header=False)
    