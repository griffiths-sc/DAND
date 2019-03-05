#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Keys containing 'fixme' will be ignored.
# 'todo' keys will be ignored.
# Keys begining with 'not' will be ignored. This includes notes but they will not be needed anyway.
# The trailing '_[number]' will be removed from all keys ending in '_[number]'.

import xml.etree.cElementTree as ET
import re
import sys

# Regular expressions
ignore_re=re.compile(r'(^not)|(^todo)|(fixme)',re.IGNORECASE)
suffix_re=re.compile(r'(_\d*$)',re.IGNORECASE)

# Mapping for replacement function
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


def fix_keys(osmfile):
    osm_file = open(osmfile, "r")
    k_count=0
    k_fixed=0
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                k_count+=1
                ok=tag.attrib['k']
                nk=fix_key(ok)
                if ok!=nk:
                    print ok,' -> ',nk
                    k_fixed+=1
    osm_file.close()
    print '\n*** Fixed '+str(k_fixed)+' out of '+str(k_count)+' keys ***'
    return

if __name__ == "__main__":
    filename=sys.argv[1]
    fix_keys(filename)
