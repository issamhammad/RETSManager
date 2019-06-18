import os
import shutil
import sys
from ..aws_settings import *
import boto3

from ..ddf_logger import *

class S3Handler:

    def __init__(self, media_dir, rets_session,format_type='STANDARD-XML'):
        try:
            self.rets_session = rets_session
            self.media_dir = media_dir
            self.format = format_type
            self.listings_path = "listings"
            self.agents_dir = "agents"
            agents_dir = self.media_dir + '/' + self.agents_dir
            self.s3 = boto3.resource('s3',aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            # self.create_dir(agents_dir)
        except Exception as e:
            logger.error(e)

    # @staticmethod
    # def create_dir(dir_path):
    #     try:
    #         if not os.path.exists(dir_path):
    #             os.makedirs(dir_path)
    #         return True
    #     except Exception as e:
    #         logger.error(e)
    #         logger.error("Failed to create DIR: %s", dir_path)
    #         return False

    def delete_dir(self,dir_path):
        try:
            found= False
            for obj in self.s3.Bucket(AWS_STORAGE_BUCKET_NAME).objects.filter(Prefix=dir_path):
                found = True
                logger.debug("Deleting DIR:%s",self.s3.Object(AWS_STORAGE_BUCKET_NAME, obj.key))
                self.s3.Object(AWS_STORAGE_BUCKET_NAME, obj.key).delete()
            return found
            # if os.path.exists(dir_path):
            #     shutil.rmtree(dir_path)
            #     return True
            # logger.error("Photo DIR Doesn't exist Delete Command was ignored: %s", dir_path)
            # return False
        except Exception as e:
            logger.error(e)
            logger.error("Failed to delete DIR: %s", dir_path)
            return False

    def delete_file(self,file_path):
        try:
            found=False
            for obj in self.s3.Bucket(AWS_STORAGE_BUCKET_NAME).objects.filter(Prefix=file_path):
                found = True
                logger.info("Deleting File:%s",self.s3.Object(AWS_STORAGE_BUCKET_NAME, obj.key))
                self.s3.Object(AWS_STORAGE_BUCKET_NAME, obj.key).delete()
            return found
        except Exception as e:
            logger.error(e)
            logger.error("Failed to delete file :%s",file_path)
            return False

    def delete_photo_dir(self,listing_id):
        try:
            dir_path = self.media_dir + '/' + self.listings_path  + '/' + str(listing_id)
            return self.delete_dir(dir_path)
        except Exception as e:
            logger.error(e)
            logger.error("Failed to delete DIR: %s", dir_path)
            return False

    def create_photo_dir(self,listing_id):
        return True #Bypass this function call, to keep similar design to ddf_media
        # try:
        #     dir_path = self.media_dir + '/' + self.listings_path  + '/' + str(listing_id)
        #     #logger.info("created DIR: %s", dir_path)
        #     return self.create_dir(dir_path)
        # except Exception as e:
        #     logger.error(e)
        #     logger.error("Failed to create DIR: %s", dir_path)
        #     return False

    # def dir_photo_exists(self,listing_id):
    #     try:
    #         dir_path = self.media_dir + '/' + self.listings_path + '/' + str(listing_id)
    #         if os.path.exists(dir_path):
    #             return True
    #         else:
    #             return False
    #     except Exception as e:
    #         logger.error(e)
    #         logger.error("Failed to check Listing DIR: %s", listing_id)
    #         return False

    def failed_downloads_append_all(self,photos_dict,listing_key,failed_downloads):
        try:
            if isinstance(photos_dict, list):
                for photo_dict in photos_dict:
                    if listing_key not in failed_downloads:
                        failed_downloads.append((listing_key, photo_dict['SequenceId']))
            else:
                if listing_key not in failed_downloads:
                    failed_downloads.append((listing_key, photos_dict['SequenceId']))
        except Exception as e:
            logger.error(e)
            logger.error("Error in appending Listing %s to Failed Downloads",listing_key)

    # def prepare_folder(self,listing_key):
    #     try:
    #         if not self.dir_photo_exists(listing_key):
    #             if not self.create_photo_dir(listing_key):
    #                 return False
    #         return True
    #     except Exception as e:
    #         logger.error(e)
    #         logger.error("Failed to prepare folder for listing:%s",listing_key)

    def save_photo(self,byte_stream,listing_id,photo_id=1,agent=False):
        try:
            if agent:
                photo_path = self.media_dir + '/' + self.agents_dir + '/' + str(listing_id) + ".jpg"
            else:
                photo_dir = self.media_dir + '/' + self.listings_path + '/' + str(listing_id)
                photo_path = photo_dir + '/' + str(photo_id) + '.jpg'

            self.s3.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(Key=photo_path, Body=byte_stream)
            # with open(photo_path, 'wb') as f:
            #     f.write(byte_stream)
            return True
        except Exception as e:
            logger.error(e)
            logger.error("Failed to save photo: %s", photo_path)
            return False

    def get_agent_photo(self,agent_id):
        photo_downloaded = False
        try:
            photo_object = self.rets_session.get_agent_photo(agent_id)
            if photo_object:
                byte_stream = photo_object[0]['content']
                if len(byte_stream) < 500:
                    logger.debug("Listing Agent Photo is less than 500 Bytes")
                else:
                    self.save_photo(byte_stream, agent_id,agent=True)
                    photo_downloaded = True
            else:
                raise Exception ("Failed to Download Agent Photo:%s",agent_id)
        except Exception as e:
            pass
            # if e != "No Object Found":
            #     logger.error(e)
        return photo_downloaded

    def get_photo(self, photo_id, listing_key, small=False):
        try:
            photo_downloaded=False
            object_type="LargePhoto" if not small else "Photo"
            photo_object = self.rets_session.get_object(resource='Property', object_type=object_type,
                                                        content_ids=listing_key, object_ids=str(photo_id))
            if photo_object:
                byte_stream = photo_object[0]['content']
                if len(byte_stream)< 500:
                    logger.debug("Error in Photo:%s for listing:%s Content:%s",photo_id, listing_key,byte_stream)
                else:
                    self.save_photo(byte_stream, listing_key, str(photo_id))
                    photo_downloaded = True
            else:
                raise Exception("Failed to download Photo:%s for Listing:%s", photo_id, listing_key)
            return photo_downloaded
        except Exception as e:
            logger.error(e)
            return photo_downloaded

    def append_failed_photo(self,photo_id,listing_key,failed_downloads):
        try:
            if (listing_key,photo_id) not in failed_downloads:
                failed_downloads.append((listing_key, photo_id))
                logger.error("Failed to Download Listing %s Photo id %s was added to failed Photos Downloads",listing_key,photo_id)
        except Exception as e:
            logger.error(e)

    def get_photos(self,listing,failed_downloads):
        try:
            listing_key = listing['ID']
            # if not self.prepare_folder(listing_key) :
            #     raise Exception("Failed to Prepare DIR")
            photos_object = self.rets_session.get_object(resource='Property', object_type="LargePhoto",
                                                        content_ids=listing_key, object_ids="*")
            for photo in photos_object:
                byte_stream = photo['content']
                if len(byte_stream)< 500:
                    logger.error("Error in Photo:%s for listing:%s", photo_id, listing_key)
                    self.append_failed_photo(photo_id, listing_key, failed_downloads)
                    continue
                else:
                    photo_id = photo['object_id']
                    self.save_photo(byte_stream,listing_key,photo_id)
            return True
        except Exception as e:
            logger.error(e)
            logger.error("Failed to get Photos for Listing:%s", listing_key)
            return False

    def compare_photo(self,listing_key,photo_dict,prev_time_stamp):
        try:
            if photo_dict['LastUpdated'] != prev_time_stamp:
                downloaded = self.get_photo(photo_dict['SequenceId'], listing_key)
                logger.debug("Photo %s for listing %s was updated, New TS: %s, OLD TS: %s", photo_dict['SequenceId'],listing_key, photo_dict['LastUpdated'],prev_time_stamp)
                if not downloaded:
                    photo_dict['LastUpdated'] = prev_time_stamp
        except Exception as e:
            logger.error(e)
            logger.error("Failed to compare photo for Listing:%s Photo:%s", listing_key,photo_dict['SequenceId'])

    def compare_photos(self,listing,prev_photos_dict):
        try:
            photos_dict_list = listing['Photo']['PropertyPhoto']
            listing_key = listing['ID']
            if isinstance(photos_dict_list,list):
                for photo_dict in photos_dict_list:
                    if photo_dict['SequenceId'] in prev_photos_dict.keys(): #not new photo (sequence id existed)
                        self.compare_photo(listing_key,photo_dict, prev_photos_dict[photo_dict['SequenceId']])
                    else: #new photo -- sequence didn't exist
                        if not self.prepare_folder(listing_key) :
                            raise Exception("Failed to Prepare DIR")
                        logger.debug("New Photo for Listing:%s",listing_key)
                        self.get_photo(photo_dict['SequenceId'], listing_key)
            else: #if only 1 photo
                   self.compare_photo(listing_key,photos_dict_list, prev_photos_dict[photos_dict_list['SequenceId']])
        except Exception as e:
            logger.debug(e)
            logger.debug("Failed to compare photos for Listing:%s", listing_key)

    def download_agent_photo(self,listing):
        try:
            listing_key = listing['ID']
            agent_dict_list = listing['AgentDetails']
            if isinstance(agent_dict_list, list):
                for agent_dict in agent_dict_list:
                    self.get_agent_photo(agent_dict['ID'])
            else:
                self.get_agent_photo(agent_dict_list['ID'])
        except Exception as e:
            logger.error(e)
            logger.error("Error in getting agent photos for Listing:%s", listing_key)

    def download_photos(self,listings,previous_photos):
        try:
            failed_downloads = []
            for listing in listings:
                try:
                    listing_key = listing['ID']
                    self.download_agent_photo(listing)
                    if 'Photo' in listing.keys() and 'PropertyPhoto' in listing['Photo']:
                        photos_dict = listing['Photo']['PropertyPhoto']
                        if listing_key in previous_photos.keys():
                            self.compare_photos(listing,previous_photos[listing_key])
                            logger.debug("Previous Photos found for listing:%s",listing_key)
                        else:
                            logger.debug("New Listing :%s",listing_key)
                            if not self.get_photos(listing,failed_downloads):
                                self.failed_downloads_append_all(photos_dict, listing_key, failed_downloads)
                    else:
                        logger.debug("Listing %s has no photos",listing_key)
                        continue
                except Exception as e:
                    logger.error(e)
                    logger.error("Failed to download Photos for Listing:%s", listing_key)
                    self.failed_downloads_append_all(photos_dict, listing_key, failed_downloads)
                    continue
            if len(failed_downloads) > 0:
                logger.warning("Failed to Download %s Photos",len(failed_downloads))
            else:
                logger.info("All New %s Listing Photos were Downloaded Successfully", len(listings))
            return True, failed_downloads
        except Exception as e:
            logger.error(e)
            logger.error("Failed to download photos for new listings")
            return False, [], []

    def delete_photos(self,listings_keys):
        try:
            for listing_key in listings_keys:
                photos_deleted = self.delete_photo_dir(listing_key)
                if not photos_deleted:
                    logger.error("Failed to delete photos for listing : %s",listing_key)
        except Exception as e:
            logger.error(e)
            logger.error("Error in Deleting old Listings Photos")

