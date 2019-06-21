import time
import traceback
from datetime import timedelta,datetime
from ..settings import *
from .ddf_media import MediaHandler
from .ddf_s3 import S3Handler
from .ddf_streamer import Streamer
from ..ddf_logger import *
from ..rets_lib import Session


class DDFClient:
    """
    A DDFClient object handles all the operations related to downloading listings data and images.
        DDFClient does the following
        1- It uses a Streamer Object (ddf_streamer.py) to handle retriving listings data
        2- It uses either MediaHandle object (ddf_media.py) or S3Handler object to download and save images either locally or to S3.

    DDFClient Constructor
    :param `media_path' : Root DIR for media files as 'string'
    :param `format_type' : Can take 'STANDARD-XML' or 'COMPACT_DECODED'. 'COMPACT-DECODED' is not tested.
    :param `s3_reader' : Boolean to determine whether the files are stored locally or using S3. (if using S3, S3 setting can be set under ../aws_settings.py)
    """

    def __init__(self, media_path,format_type='STANDARD-XML',s3_reader=True):
        try:
            self.rets_session = Session(login_url, username, password)
            if not s3_reader:
                self.media_handler = MediaHandler(media_path,self.rets_session)
            else:
                self.media_handler = S3Handler(media_path,self.rets_session)
            self.streamer = Streamer(self.rets_session,format_type)
            self.format = format_type
        except Exception as e:
            logger.error(e)

    def login(self):
        """Uses Streamer Object to login"""
        return self.streamer.login()
             
    def logout(self):
        """Uses Streamer Object to logout"""
        return self.streamer.logout()

    @staticmethod
    def get_gmt_time(**kwargs):
        """Gets GMT time and converts it to 'YYYY-MM-DDTHH:MM:SSZ' format"""
        time_now = datetime.utcnow()
        time_diff = timedelta(days=3)
        time_adj = time_now - time_diff
        return time_adj.strftime("%Y-%m-%dT%H:%M:%SZ")


    def validate_time_update(self,last_update,ignore_restrictions=False):
        """Validates last_update time stamp. Raises an error if the time is in the future
            Also, if restrictions are applied it confirms that timestamp is valid and is not too old based on MAX_UPDATE_TIME under (../setting.py)
            This restriction is required by certain MLS servers"""

        try:
            time_format = '%Y-%m-%dT%H:%M:%SZ'
            time_now = time.mktime(time.strptime(self.get_gmt_time(),time_format))
            update_time_stripped = time.mktime(time.strptime(last_update,time_format))
            time_difference = time_now - update_time_stripped
            if time_difference > MAX_UPDATE_TIME and not ignore_restrictions:
                logger.error("Last Update Time exceeded allowed limit of %s seconds, Last Update=%s", MAX_UPDATE_TIME,last_update)
                return False
            elif time_difference < 0:
                logger.error("Last Update time is a future time, value is invalid Last Update=%s", last_update)
                return False
            return True
        except Exception as e:
            logger.error(e)
            logger.error("Failed to validate time, please re-check your last_update value, last_update=%s time format should be=%s",last_update, time_format)
            return False


    def get_listings_keys(self, input_list):
        """Returns a list of listings ids (string) from a list of dictionaries containing all listings information"""

        if self.format == 'COMPACT-DECODED':
            id_key = 'ListingKey'
        else:
            id_key='ID'
        try:
            listings_keys = []
            for item in input_list:
                try:
                    listings_keys.append(item[id_key])
                except Exception as e:
                    logger.error(e)
                    logger.error("%s was not found in :%s",id_key,item)
            return listings_keys
        except Exception as e:
            traceback.print_exc()
            logger.error(e)
            logger.error("Error in getting listings keys from input list")
            return []


    def download_by_id(self,listings_keys,limit=None,search_class='Property'):
        """Called by 'download_remaining_listing' to retrive listings by id
            Parameters:
                1- listing_keys: a list of listing_keys (string)
                2- The offset for the first record.The API is limited to 100 records per call, so incase there is a 1000 records since that timestamp. 10 API calls are required with offsets
                    0,100,200... 900.
                3- limit: The limit for number of active records to be retrived. Set to SESSION_LISTINGS_COUNT by default
            Returns (True,listings) if the call was successful"""

        listings=[]
        if limit:
            listings_keys = listings_keys[:limit]
        try:
            #loop in group of 100s
            for offset in range(0, len(listings_keys), SESSION_LISTINGS_COUNT):
                logger.info("Downloading Listings found by ID with Offset:%s-%s", offset,
                            offset + SESSION_LISTINGS_COUNT)
                try:
                    new_listings, count = self.streamer.retrieve_by_id(
                        listings_keys[offset:offset + SESSION_LISTINGS_COUNT]) #use offset to get each group of 100

                    if not isinstance(new_listings, list): #convert to list if not
                        new_listings = [new_listings]

                    listings = listings + new_listings
                except Exception as e:
                    logger.error(e)
                    logger.error("Error in downloading Listings found by ID with offset:%s-%s for class :%s", offset,
                                 offset + SESSION_LISTINGS_COUNT,search_class)
            return True,listings
        except Exception as e:
            logger.error(e)
            logger.error("Error in for-loop to download Listings by ID")
            return False, []


    def download_active_listings(self,last_update,limit=None,offset=None):
        """Retrives all active listings since a time_stamp (last_update)
            Parameters:
                1- last_update: a timestamp in the form of 'YYYY-MM-DDTHH:MM:SSZ"
                2- offset: The offset for the first record.The API is limited to 100 records per call, so incase there is a 1000 records since that timestamp. 10 API calls are required with offsets
                    0,100,200... 900.
                3- limit: The limit for number of active records to be retrived. Set to SESSION_LISTINGS_COUNT by default
            Returns (True,listings) if the call was successful"""
        try:
            logger.debug("Attempting to download first new %s active listings at %s",SESSION_LISTINGS_COUNT,last_update)
            try:
                #get active records, first 100.
                listings,count=self.streamer.retrieve_active_records(last_update,limit=limit,offset=offset)
                if not isinstance(listings,list): #make it a list if not, example: 1 item only
                    listings = [listings]
                if int(count) < 0: #if count is less than zero terminate
                    logger.error("Failed to retrieve active records")
                    return False, []
                if limit and limit < int(count): #if limit is applied and limit is less than count
                    count = limit #Used for logging
            except Exception as e:
                logger.error(e)
                logger.error("Failed to download new active listings at %s",last_update)
                return False,[]
            logger.info("%s active listings found since %s",int(count),last_update)
            try:
                # if count larger than RETS SESSION MAX (100)
                if int(count) > SESSION_LISTINGS_COUNT:
                    #get group of 100 or less each time using an offset of 100
                    for offset in range(SESSION_LISTINGS_COUNT+1,int(count),SESSION_LISTINGS_COUNT):
                        logger.debug("Attempting to download new active listings Offset:%s-%s", offset,offset+SESSION_LISTINGS_COUNT )
                        try:
                            new_listings,new_count= self.streamer.retrieve_active_records(last_update,limit=limit,offset=offset)
                        except Exception as e:
                            logger.error(e)
                            logger.error("Failed to download new active listings Offset:%s-%s", offset,
                                        offset + SESSION_LISTINGS_COUNT)
                        listings=listings+ new_listings #append the new group of listings
            except Exception as e:
                logger.error(e)
                logger.error("Failed to download active listing exceeding %s", SESSION_LISTINGS_COUNT)
                return False,[]

            if len(listings) != int(count): #Warning if count doesn't match len. No need to terminate.
                                            # Listing will be found by ID.
                logger.warning("Downloaded Active Listings are %s while COUNT is %s",len(listings),int(count))
            else:
                logger.info("%s new active listing successfully downloaded",len(listings))
                #self.listings=listings
        except Exception as e:
            logger.error(e)
            return False,[]
        return True,listings


    def download_remaining_listings(self,previous_listings_keys=[],limit=None):
        """Gets listings found to be missing by comparing db listing + active listing againts the master list
        calls download_by_id to download missing listings
        also it finds removed listings and return a list of them
        Parameters:
            1- previous listings_keys: a list of listings keys that exists in the database
            2- limit: The limit for number of active records to be retrived. Set to SESSION_LISTINGS_COUNT by default
        """

        removed_listings_keys=[]
        try:
            logger.info("Attempting to download listings by id")
            try:
                #get master list of all listings from DDF
                master_list,count = self.streamer.retrieve_master_list()
                if not isinstance(master_list,list):
                    master_list = [master_list]
                if int(count) < 0:
                    logger.error("Failed to Retrieve Master List")
                    return False, [], []
            except Exception as e:
                logger.error(e)
                logger.error("Failed to Retrieve Master List")
                return False, [], []
            try:
                if master_list:
                    master_listings_keys = self.get_listings_keys(master_list)
                    if not master_listings_keys:
                        logger.error("Failed to extract master listing keys")
                        return False, [], []
                else:
                    logger.error("Master list was empty")
                    return False, [], []

            except Exception as e:
                logger.error(e)
                logger.error("Failed to get listing keys from Master List")
                return False, [], []

            #get list of missing listings keys than are neither in db nor in active listings
            added_listings_keys = [listing_key for listing_key in master_listings_keys if listing_key not in previous_listings_keys]
            #get a list of removed listings than are not in master list but in db
            removed_listings_keys= [listing_key for listing_key in previous_listings_keys if listing_key not in master_listings_keys]
            logger.info("Listings found to be added by ID are: %s",len(added_listings_keys))
            logger.info("Listings found to be removed by ID are: %s", len(removed_listings_keys))

            #download missing listings by ID
            downloaded_by_id,listings= self.download_by_id(added_listings_keys,limit)

            #if an error during downloading by ID.
            if not downloaded_by_id:
                logger.error("Failed to Download by ID")
                return False, [], []

        except Exception as e:
            logger.error(e)
        logger.info("Successfully updated all listings by ID")
        return True,listings,removed_listings_keys


    def update_listings(self,last_update,previous_listings_keys=[],limit=None,offset=None):

        """This function does the following:
            1-Gets all active listings since last_update timestamp
            2- Download any remaining missing listings by ID after comparing the master list against the previous_listing_keys
         The function will call download_active_listing and download_remaining_listing functions to perform these tasks.

        Parameters:
            1- last_update: a timestamp in the form of 'YYYY-MM-DDTHH:MM:SSZ"
            2- offset: The offset for the first record.The API is limited to 100 records per call, so incase there is a 1000 records since that timestamp. 10 API calls are required with offsets
                0,100,200... 900.
            3- limit: The limit for number of active records to be retrived. Set to SESSION_LISTINGS_COUNT by default
            4- previous_listing_keys: a list of strings for the existing listings ids

        Returns:
            1- Boolean (True/False) if the operation was successful/failed.
            2- a list of dictionaries for listings
            3- a list of strings for the removed listings ids.
        """

        listings=[]
        logger.info("Update Listings Started")
        try:
            #Download updated listings since lastupdate.
            active_listings_downloaded,active_listings = self.download_active_listings(last_update,limit=limit,offset=offset)
            logger.debug("Total Active Listings: %s", len(active_listings))
            listings = listings + active_listings
            if not active_listings_downloaded: #if failed to get active listings terminate
                logger.error("Failed to Download Active Listings")
                logger.error("Update was terminated")
                return False,[],[]
            else:
                if limit: #if limit is applied
                    if len(listings) >= limit: #if limit is reached skip download by ID for missing listings
                        logger.warning("Download by ID is skipped as limit is reached through active listing search")
                        return True,listings,[]
                    else: #if limit is not reached, calculate the remaining limit for downloading by ID
                        limit = limit - len(listings)
                try:
                    if active_listings: #if new active listings found
                        active_listings_keys = self.get_listings_keys(active_listings) #get IDs in a list
                        if not active_listings_keys: #if failed to get IDs
                            logger("Failed to extract active listing keys") #Terminate
                            return False, [], []
                    else: #if no new listing founds
                        active_listings_keys=[] #empty List

                    #current available listings = db listings + listings since last update
                    available_listings_keys = active_listings_keys + previous_listings_keys

                    #download any missing listing other than the available, uses master list to compare againts available listings
                    listings_by_id_downloaded,listings_by_id,removed_listings_key = self.download_remaining_listings(available_listings_keys,limit=limit)

                    if not listings_by_id_downloaded: #if failed to download remaining by ID
                        logger.error("Failed to Download Listings By ID")
                        logger.error("Update was terminated")
                        return False,[],[] #terminate
                    else:
                        logger.info("Total Listings Downloaded By ID: %s", len(listings_by_id))
                        listings = listings + listings_by_id
                        logger.info("Total Listings Downloaded : %s",len(listings))
                except Exception as e:
                    logger.error(e)
                    logger.error("Error in Updating Listings By ID")
                    return False,[],[]
        except Exception as e:
            logger.error(e)
            logger.error("Error in Updating Active Listings")
            return False,[],[]
        logger.info("Update Listings were Successful")
        return True, listings,removed_listings_key

    #retry to download failed Photos
    def retry_failed_photos_downloads(self,failed_photos_downloads,retries =PHOTOS_DOWNLOAD_RETRIES):
        """This function is for retrying to download photos that previously failed to download
            Parameters:
            1- fail_photos_downloads: a list of tuples representing (listing_id,photo_id) for each photo.
            2- retries: The number of attempts for retrying before giving up.
            Returns (Boolean whether the operations has worked or failed
        """
        try:
            new_failed_photos_download = []
            for retry in range(retries):
                if failed_photos_downloads:
                    logger.info("Retry %s to Download Failed Photos",(retry+1))
                    logger.info("Failed Photos count: %s",len(failed_photos_downloads))
                else:
                    logger.info("No Remaining Failed Photos Downloads")
                    return True
                for listing_key, photo_id in failed_photos_downloads:
                    if not self.media_handler.get_photo(listing_key, photo_id):
                        new_failed_photos_download.append((listing_key, photo_id))
                failed_photos_downloads = new_failed_photos_download
                new_failed_photos_download = []
            return False
        except Exception as e:
            logger.error(e)
            logger.error("Failed to Retry Downloading Failed Photos")
            return False


    def remove_failed_photos_listings(self,listings,failed_photos_downloads):
        """Deletes listings that has photos that failed to download
            Parameters;
                1- listings: a list of listing dictionaries.
                2- failed_photos_downloads: a list tuples represtings (listing_id,photo_id) for failed photos.
            Returns Boolean indicating success or failure.
        """
        try:
            failed_downloads_keys = [key for (key,photo_id) in failed_photos_downloads]
            for listing in listings:
                listing_key = listing['ID']
                if listing_key in failed_downloads_keys:
                    listings.remove(listing)
                    logger.info("Removed Listing %s from Listings as photos failed to download",listing_key)
            return True
        except Exception as e:
            logger.error(e)
            logger.error("Failed to Remove Listings with Failed Downloads from Downloaded Listings")
            return False


    def remove_old_listings_photos(self,removed_listings_keys):
        """removed photos for expired listings based on removed_lisings_keys parameter."""
        return self.media_handler.delete_photos(removed_listings_keys)


    def update_photos(self,listings,previous_photos={},skip_photos=False):
        """Responsible for downloading or updating all photos based on the list of listings
            Parameters;
                1- listings: a list of listing dictionaries.
                2- previous_photos: a dictionary with keys representing listing ids and values representing the list of photo ids.
                3- skip_photos: Boolean to skip the photo update all together.
            Returns Boolean indicating success or failure.
        """
        try:
            if not skip_photos: #if update is not skipped

                #photos_downloaded: boolean. failed_photos_downloads and redownloads: lists
                photos_downloaded, failed_photos_downloads = \
                    self.media_handler.download_photos(listings,previous_photos)

                if not photos_downloaded: #if failed to download returned terminate function
                    logger.error("Update was terminated due to failure in Downloading photos")
                    return False
                else: #if photos downloaded.

                    #failed_photos_downloads: New Photos that failed to download. Listings with these photos will
                    #be removed if retry failed. They will be recognized by the sync photos manager function.

                    if failed_photos_downloads:
                        logger.info("Retry to Download Failed Downloads")
                        #self.retry_failed_photos_downloads(failed_photos_downloads)
                        if self.remove_failed_photos_listings(listings,failed_photos_downloads):
                            return True
                    else:
                        return True
            else:
                logger.warning("Photos Download skipped by user")
            return True
        except Exception as e:
            logger.error(e)
            logger.error("Failed to Update Photos")
            return False


    def update(self,last_update, previous_listings_keys ,limit=None,offset=None,ignore_restrictions = False,skip_photos=False,previous_photos={}):
        """Completes an entire update operation including data and photos
            Parameters:
                1- last_update: previous update timestamp, previous_listing_keys:
                2- previous_listing_keys: list of the current listing keys that exists in the db,
                3- limit: max 100.. the MLS API is limited to 100 full listings records per call. Limit can be lowered if needed
                4- offset: The offset for the first record.The API is limited to 100 records per call, so incase there is a 1000 records since that timestamp. 10 API calls are required with offsets
                    0,100,200... 900.,
                5- ignore_restrictions: restrictions on timestamp date and a forced non empty previous listing keys,
                6-skip_photos: update with/without photos
                7- previous_photos: a dictionary with keys representing listing ids and values representing the list of photo ids.

            Returns:
                updated_data dictionary
        """
        #defines default dictionary
        updated_data = {"Pass": False, "Listings:":[] , "Removed_Listings": [],"LastUpdate":self.get_gmt_time(),
                        "Previous_Listings": previous_listings_keys,"Limit":limit,"Offset":offset}
        try:
            # if empty prev_listing restrictions are not ignored terminate update.
            if not previous_listings_keys and not ignore_restrictions:
                logger.error("Previous listing keys array is empty, update was terminated")
                return updated_data

            # if invalid or old timestamp restrictions are not ignored terminate update.
            if not self.validate_time_update(last_update,ignore_restrictions):
                logger.error("Failed to validate last_update time, update was terminated")
                return updated_data

            #listing_updated: Boolean, listings: updated listings , removed_listings_keys: list of removed listings ids
            listing_updated, listings, removed_listings_keys = \
                self.update_listings(last_update,previous_listings_keys,limit=limit,offset=offset)

            #if listing updated successfully
            if listing_updated:
                logger.info("Listing Update Completed")

                #photos_updated: Boolean, failed_photos_redownloads: list
                photos_updated = self.update_photos(listings,previous_photos=previous_photos,skip_photos=skip_photos)

                #if successfuly got listings and downloaded photos, update is successfull, return to manager for db update
                if photos_updated:
                    updated_data["Pass"] = True
                    updated_data["Listings"] = listings
                    updated_data["Removed_Listings"] = removed_listings_keys
                    logger.info("Data Update was successful")

            return updated_data #return updated_data dict
        except Exception as e:
            logger.error(e)
            logger.error("Update Failed")
            return updated_data

