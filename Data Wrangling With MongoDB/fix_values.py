#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Problematic/unwanted characters will be removed.
# Abbreviated street names will be replaced with the correct full name.
# Each word will modified to start with a capital letter.
# Welsh names containing *'Y'*, *'Yr'* and *'Yn'* will be hyphenated, for example *'Ael Y Bryn'* becomes *'Ael-Y-Bryn'*.

import xml.etree.cElementTree as ET
import re
import sys

# Values to be cleaned
to_be_cleaned=['addr:street', 'name', 'amenity', 'cuisine']

# Regular expressions
unwanted_re=re.compile(r'[\[\]().\']|(amp;)')
postcode_re=re.compile(r'\w+\d+\s*\d+\w+',re.IGNORECASE)

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
        
def fix_value(v):
    if not ignore_vals(v):
        v=remove_unwanted(v)
        v=capitalise(v)
        v=update_abbr(v)
        v=update_welsh(v)
    return v

def fix_values(osmfile):
    osm_file=open(osmfile,"r")
    v_count=0
    v_fixed=0
    for event,elem in ET.iterparse(osm_file,events=("start",)):
        if elem.tag=="node" or elem.tag=="way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] in to_be_cleaned:
                    v_count+=1
                    ov=tag.attrib['v']
                    nv=fix_value(ov)
                    if ov!=nv:
                        print ov,' -> ',nv
                        v_fixed+=1
    osm_file.close()
    print '\n*** Fixed '+str(v_fixed)+' out of '+str(v_count)+' values ***'
    return


if __name__ == "__main__":
    filename=sys.argv[1]
    fix_values(filename)
