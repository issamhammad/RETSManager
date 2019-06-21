import json

from ddf_manager.settings import *
from ..ddf_logger import logger


class Streamer:
    """
    A Streamer Object uses rets_lib Session Object (under rets_lib/session.py) to do the following:
        1- Retrive the master list of all the ids of all the available listing
        2- Retrive all active listings since a time stamp.
        3- Manual retrival of listing by id.

    Streamer Constructor
    :param `rets_session`: rets_lib Session Object
    :param `format_type' : Can take 'STANDARD-XML' or 'COMPACT_DECODED'. 'COMPACT-DECODED' is not tested.
    """

    def __init__(self,rets_session,format_type='STANDARD-XML'):
        try:
            self.format = format_type
            self.rets_session = rets_session
        except Exception as e:
            logger.error(e)

    def login(self):
        """
        Returns True if login successful.
        """
        try:
            logger_seperator = "=" * 75
            logger.info(logger_seperator)
            login_passed = self.rets_session.login()
            if login_passed:
                logger.info("Login Successful")
                return True
            else:
                logger.info("Login Failed")
                return False
        except Exception as e:
            logger.error(e)
            return False

    def logout(self):
        """
        Returns True if logout successful.
        """
        try:
            logout_passed = self.rets_session.logout()
            if logout_passed:
                logger.info("Logout Successful")
                return True
            else:
                logger.info("Logout Failed")
                return False
        except Exception as e:
            logger.error(e)
            return False

    def retrieve_master_list(self):
        """
        Retrives the Master List containing all available listings ids. This doesn't return the full listing details, just the ids.
        Returns:
            1- a list of dictionaries containing the ids and other meta data.
            2- The count (as per the source) as int.
        """
        try:
            count = '-1'
            master_list = self.rets_session.search(resource='Property', resource_class='Property', dmql_query='(ID=*)',format=self.format)
            if not master_list:
                logger.error("Failed to retreive master_list, returned value:%s",str(master_list))
                return [],count

            if master_list['ReplyCode'] != '0':
                logger.error("Search Failed by RETS Server, Returned Code: %s, Message: %s",master_list['ReplyCode'],master_list['ReplyText'])
                return [],count

            if len(master_list["Data"]) != int(master_list["Count"]):
                logger.warning("Master list Count is:%s while master list len is :%s", int(master_list["Count"]),len(master_list["Data"]))

            logger.info("Master List Retrieved with %s Records",int(master_list["Count"]))

            count = master_list["Count"]
            return master_list["Data"], count
        except Exception as e:
            logger.error(e)
            logger.error("Error in Retrieving Master List")
            return [],count

    def retrieve_active_records(self,last_update,offset=0,limit=SESSION_LISTINGS_COUNT):
        """
        Retrives the full details of the active records since a time stamp (last_update).
        Since the MLS API is limited to 100 records per call. The offset parameter can be used to adjust the starting record and move it accordingly in a loop
        Parameters:
            1- last_update: a timestamp in the form of 'YYYY-MM-DDTHH:MM:SSZ"
            2- The offset for the first record.The API is limited to 100 records per call, so incase there is a 1000 records since that timestamp. 10 API calls are required with offsets
                0,100,200... 900.
            3- limit: The limit for number of active records to be retrived. Set to SESSION_LISTINGS_COUNT by default
        Returns:
            1- a list of dictionaries containing the full listing details
            2- The count (as per the source) as int.
        """
        try:
            count = '-1'
            last_updated_query = '(LastUpdated=' + last_update + ')'
            new_listings = self.rets_session.search(resource='Property', resource_class='Property', dmql_query=last_updated_query, limit=limit,offset=offset,format=self.format)
            if new_listings['ReplyCode'] == '20201':
                logger.warning("No Active Records Founds")
                count = '0'
                return [],count
            elif new_listings['ReplyCode'] != '0':
                logger.error("RETS Server Failure, Returned Code: %s, Message: %s",new_listings['ReplyCode'],new_listings['ReplyText'])
                return [],count

            if new_listings:
                logger.debug("Retrieved %s Active Listings", len(new_listings["Data"]))
                self.listings=new_listings["Data"]
                count = new_listings["Count"]

            else:
                logger.warning("No Active Listing found or Failed to retreive active records")
                return [],count
            return self.listings,count

        except Exception as e:
            logger.error(e)
            logger.error("Failed to retreive active listings")
            return [],count

    def retrieve_by_id(self,ids_list,search_class='Property'):
        """
        Retrives the full details of listings according to a list of ids.
        Since the MLS API is limited to 100 records per call. The offset parameter can be used to adjust the starting record and move it accordingly in a loop
        Parameters:
            1- id_list: a list of ids as as string.
            2- search_class: Only "Property is used for this framework' other classes can be used in the future based on the MLS structure.
        Returns:
            1- a list of dictionaries containing the full listing details
            2- The count (as per the source) as int.
        """
        try:
            count = '-1'
            if ids_list:
                query = '(ID=' + ','.join(map(str,ids_list)) + ')'
                new_listings = self.rets_session.search(resource=search_class, resource_class=search_class ,dmql_query=query, limit=None,format=self.format)
            else:
                logger.error("ids_list argument is an empty list")

            if not new_listings:
                logger.error("Retreive by ID search returned empty values from the Server or Library")
                return [], count

            if new_listings['ReplyCode'] == '20201':
                logger.error("No Records by ID Founds")
                return [],count #Returning count as -1 as this should not return empty list

            elif new_listings['ReplyCode'] != '0':
                logger.error("Search Failed by RETS Server, Returned Code:%s, Message:%s",new_listings['ReplyCode'],new_listings['ReplyText'])
                return [],count

            if new_listings and isinstance(new_listings["Data"],list):
                logger.info("Retrieved %s Listings by ID", len(new_listings["Data"]))
                self.listings=new_listings["Data"]
                count = new_listings["Count"]
            else:
                logger.error("Failed to retreive Listings, returned value:%s ", str(new_listings["Data"]))
                return [], count

            return self.listings,count

        except Exception as e:
            logger.error(e)
            logger.error("Failed to retreive listings by id")
            return [], count