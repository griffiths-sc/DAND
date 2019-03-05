#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Requires installation of postcode.io library

from lib import PostCodeClient
import json

client = PostCodeClient()

def nearest_postcode(longitude=None,latitude=None):
    # Return nearest postcode and distance
    data=json.loads(client.getLocationBasedPostcodes(lon=str(longitude),lang=str(latitude)))
    if data['status']==200:
        # Return the first (closest) result
        return (data['result'][0]['postcode'],round(data['result'][0]['distance'],2))
    else:
        return None
    
def validate_postcode(postcode):
    # Return True if postcode is valid, False otherwise
    data=json.loads(client.validatePostCode(postcode))
    if data['status']==200:
        return (data['result'])
    else:
        return False


if __name__ == "__main__":
    print '\nNearest postcode to longitude -2.9800493 and latitude=53.1721903:'
    nearest_postcode(longitude=-2.9800493,latitude=53.1721903)
    print '\nDoes CH4 0DR exist?'
    validate_postcode('CH4 0DR')
    print '\nDoes CH9 0ZZ exist?'
    validate_postcode('CH9 0ZZ')
