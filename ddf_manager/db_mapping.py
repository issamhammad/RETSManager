from web_app.models import *

###This file is used to map the values retrived from the ddf_client to the Django database.
### Each list contains a tuple or more representing the following:
###(Table Name in DDF, Table Object in DB, Table fields key in db_fields, children dictionary as per DDF Standard)


from web_app.models import *

building_children = [
    ('Rooms',Room,'room_fields','Room'),
]

office_children = [
    ('Address', Address, 'address_fields',None),
    ('Phones', Phone, 'phones_fields','Phone'),
    ('Websites', Website, 'websites_fields','Website'),
]

agent_children = [
    ('Address', Address, 'address_fields', None),
    ('Phones', Phone, 'phones_fields','Phone'),
    ('Websites', Website, 'phones_fields','Website'),
    #('Specialties', AgentSpecialities, 'agent_specialties_fields', 'Specialty'),
    #('Designations ', AgentSpecialities, 'agent_designations_fields','Designation'),
    #('Languages ', AgentLanguages,'agent_languages_fields','Language'),
    #('TradingAreas ', AgentTradingAreas,'agent_trading_areas_fields','TradingArea'),
]

#defines only simple children that doesn't children
property_children = [
    ('Photo',PropertyPhoto,'property_photo_fields','PropertyPhoto'),
    ('Address', Address, 'address_fields',None),
    ('Land', Land, 'land_fields',None),
    ('Business', Business, 'business_fields',None),
    ('AlternateURL', AlternateURL, 'alternate_url_fields',None),
    ('ParkingSpaces', Parking, 'parking_fields', 'Parking'),
    ('UtilitiesAvailable', Utility, 'utility_fields', 'Utility'),
    ('OpenHouse', Event, 'event_fields', 'Event'),


]
#used to rename fields
rename_fields_dict = {'ID':'DDF_ID','#text':'text'}

#fields names as per the model for each table
db_fields = {
    'property_fields' : [f.name for f in Property._meta.get_fields()],
    'property_info_fields': [f.name for f in PropertyInfo._meta.get_fields()],
    'building_fields' : [f.name for f in Building._meta.get_fields()],
    'room_fields' : [f.name for f in Room._meta.get_fields()],
    'land_fields' : [f.name for f in Land._meta.get_fields()],
    'address_fields' : [f.name for f in Address._meta.get_fields()],
    'business_fields' : [f.name for f in Business._meta.get_fields()],
    'alternate_url_fields' : [f.name for f in AlternateURL._meta.get_fields()],
    'parking_fields' : [f.name for f in Parking._meta.get_fields()],
    'property_photo_fields' : [f.name for f in PropertyPhoto._meta.get_fields()],
    'utility_fields' : [f.name for f in Utility._meta.get_fields()],
    'event_fields' : [f.name for f in Event._meta.get_fields()],
    'agent_details_fields' : [f.name for f in AgentDetails._meta.get_fields()],
    'office_details_fields' : [f.name for f in OfficeDetails._meta.get_fields()],
    'phones_fields': [f.name for f in Phone._meta.get_fields()],
    'websites_fields': [f.name for f in Website._meta.get_fields()],
    #'agent_specialties_fields': [f.name for f in AgentSpecialities._meta.get_fields()],
    #'agent_designations_fields': [f.name for f in AgentDesignations._meta.get_fields()],
    #'agent_languages_fields': [f.name for f in AgentLanguages._meta.get_fields()],
    #'agent_trading_areas_fields': [f.name for f in AgentTradingAreas._meta.get_fields()],
}
