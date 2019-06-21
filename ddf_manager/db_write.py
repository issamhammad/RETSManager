from .db_mapping import *
from .db_summary import *

##This file maps the DDF data retrived by the ddf_client to the proper table in the database.

##To understand the structure of the mapping in this files, Please refer to the DDF documenation under:
##https://www.crea.ca/wp-content/uploads/2016/02/Data_Distribution_Facility_Data_Feed_Technical_Documentation.pdf

#filter_fields: used to get fields that are neither a list nor a dictionary elements for saving in db. Also renames the fields if needed.
def filter_fields(input,fields,rename_fields):
    output = {}
    if input:
        for key in input.keys():
            #if list or dictionary skip
            if not input[key] or isinstance(input[key],list) or isinstance(input[key],dict):
                continue
            #rename if in rename_fields
            elif key in rename_fields:
                output[rename_fields[key]] = input[key]
            #add to output if a single field
            elif key in fields:
                output[key] = input[key]
    return output

#update_table: saves a recorded a db table.
#parameters(table in ddf record, Table db Object, db_field, renamed_fields,**kwargs is used to pass parent object by assignment)
def update_table(table,TABLE,table_fields,rename_fields=rename_fields_dict,**kwargs):
    record_obj = None
    if table:
        if isinstance(table, list):
            for record in table:
                record_filtered = filter_fields(record, table_fields,rename_fields=rename_fields)
                if record_filtered:
                    record_obj = TABLE(**record_filtered, **kwargs)
                    record_obj.save()
        else:
            record = table
            record_filtered = filter_fields(record, table_fields,rename_fields=rename_fields)
            if record_filtered:
                record_obj = TABLE(**record_filtered, **kwargs)
                record_obj.save()
    return record_obj

#check_if_exists: used for checking if a listing exists in db.
#listing as a dict, previous_listing_keys as a list of strings
def check_if_exists(listing,previous_listing_keys):
    if listing['ID'] in previous_listing_keys:
        obj = Property.objects.get(DDF_ID=listing['ID'])
        if obj.LastUpdated == listing['LastUpdated']:
            return True,False,None
        creation_date = obj.CreationDate
        obj.delete()
        return True, True,creation_date
    else:
        return False,False,None

##Maps all DDF tables that are children of the 'office' table in DDF to the db
def add_office_children(office,office_obj):
    for (item,itemClass,item_db_fields,single_element_dict) in office_children:
        if item in office.keys():
            if isinstance(office[item], dict) and single_element_dict in office[item].keys():
                table = office[item][single_element_dict]
            else:
                table = office[item]
            update_table(table, itemClass, db_fields[item_db_fields],Office=office_obj)

##Maps agent details table from the DDF to the db
def add_agents_details(agents,property_obj):
    if not isinstance(agents,list):
        agents = [agents]

    for agent in agents:
        agent_obj = update_table(agent, AgentDetails, db_fields['agent_details_fields'],Property=property_obj)

        if 'Office' in agent.keys():
            office_obj = update_table(agent['Office'], OfficeDetails, db_fields['office_details_fields'], Agent=agent_obj)

            if office_obj:
                add_office_children(agent['Office'],office_obj)

        for (item,itemClass,item_db_fields,single_element_dict) in agent_children:
            if item in agent.keys():
                if isinstance(agent[item],dict) and single_element_dict in agent[item].keys():
                    table = agent[item][single_element_dict]
                else:
                    table = agent[item]
                update_table(table, itemClass, db_fields[item_db_fields],Agent=agent_obj)

##Maps all DDF tables that are children of the 'building' table in DDF to the db
def add_building_children(building,building_obj,property_obj):

    #add children as per db_mapping
    for (item, itemClass, item_db_fields, single_element_dict) in building_children:
        if item in building.keys():
            if isinstance(building[item], dict) and single_element_dict in building[item].keys():
                table = building[item][single_element_dict]
            else:
                table = building[item]
            update_table(table, itemClass, db_fields[item_db_fields],Property=property_obj)

##Maps all DDF tables that are children of the 'property' table in DDF to the db
def add_property_children(listing,property_obj):

    #property_info is PropertyDetails Fields in DDF
    property_info_obj = update_table(listing, PropertyInfo, db_fields['property_info_fields'],Property=property_obj)

    if 'Building' in listing.keys():
        building_obj = update_table(listing['Building'], Building, db_fields['building_fields'],Property=property_obj)

        if building_obj:
            add_building_children(listing['Building'],building_obj,property_obj)

    if 'AgentDetails' in listing.keys():
        add_agents_details(listing['AgentDetails'],property_obj)

    #add children as per db_mapping
    for (item,itemClass,item_db_fields,single_element_dict) in property_children:
        if item in listing.keys():
            #Used to assign Children child as some has that in DDF Definition for Example Rooms,Photos.
            if isinstance(listing[item], dict) and single_element_dict in listing[item].keys():
                table = listing[item][single_element_dict]
                #print (table)
            else:
                #if no extra level is there update direct child
                table = listing[item]
            update_table(table, itemClass, db_fields[item_db_fields],Property=property_obj)

#update_records is the main function to update the DDF data which is structured as dictionary to the db tables.
#It received 'new_listings' as a list of dictionaries and it applied the db updates accordingly.
#This function updates only records and is not responsible on handling photos.
def update_records(new_listings):
    #read existings keys based an IDs
    previous_listings_keys = list(Property.objects.values_list('DDF_ID', flat=True).filter())

    new_listings_count = 0
    updated_count = 0
    not_updated_count = 0
    missing_address_count = 0

    for listing in new_listings:
        #delete if record is already in db.
        try:
            listing_exist, listing_updated,creation_date = check_if_exists(listing,previous_listings_keys)
            #used to keep track of orginal creation date
            if listing_exist:
                if listing_updated:
                    listing['CreationDate'] = creation_date
                    logger.debug("Listing %s is updated old ts:%s new ts:%s",listing['ID'],creation_date,listing['LastUpdated'])
                    updated_count+=1
                else:
                    logger.debug("Listing %s found without updates",listing['ID'])
                    not_updated_count+=1
                    continue
            else:
                logger.debug("Creating New Listing %s",listing['ID'])
                listing['CreationDate'] = listing['LastUpdated']
                new_listings_count+=1

            # listing['Multi']=False
            #add property_fields
            property_obj = update_table(listing,Property,db_fields['property_fields'])

            if property_obj:
                #add the rest of the records
                add_property_children(listing,property_obj)
                if 'Address' in listing.keys():
                    add_geolocation(property_obj)
                else:
                    missing_address_count += 1
            else:
                logger.error("Couldn't create Property object for Listing: %s", listing)
        except Exception as e:
            logger.info(e)
            logger.info("Error in updating record for listing: %s",listing['ID'])
            continue

    logger.info("New Listings       : %s",new_listings_count)
    logger.info("Updated Listings   : %s", updated_count)
    logger.info("No Change Listings : %s", not_updated_count)
    logger.info("No Address Listings: %s",missing_address_count)

    return True