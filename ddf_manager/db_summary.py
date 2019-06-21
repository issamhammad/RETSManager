import re

###This file is used to add additional information that doesn't exist in the MLS data. Here geolocation is added using a geocoder.

import geocoder
from web_app.models import *
from .ddf_logger import *


def add_geolocation(listing):
    try:
        full_address = listing.Address.StreetAddress + " " + \
                       listing.Address.City + " " + \
                       listing.Address.Province + " " + \
                       listing.Address.PostalCode
        # "CANADA" #Should be removed
        geocoding_values = geocoder.arcgis(full_address)
        Geolocation.objects.update_or_create(Property=listing, defaults={'lng': geocoding_values.json['lng'],
                                                                         'lat': geocoding_values.json['lat']})
        # print(count)
    except Exception as e:
        logger.error(e)
        logger.error("Error in adding Geolocations for listing: %s", listing.DDF_ID)


def add_geolocation_all():
    try:
        #count=0
        listings = Property.objects.all().filter(PropertyType='Single Family')
        for listing in listings:
            add_geolocation(listing)
            #count += 1
            # print(count)
    except Exception as e:
        logger.error(e)
        logger.error("Error in adding Geolocations for all listings")


