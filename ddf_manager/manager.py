import pickle
import boto3
import os
from web_app.models import Property, PropertyInfo, AgentDetails, DDF_LastUpdate
# from RETS_Manager.settings_aws import *
from .aws_settings import *
from . import db_write
#from .db_summary import *
from .ddf_logger import *
from .ddf_client.ddf_client import DDFClient
from .settings import *  # Local ddf_manager Settings.
from django.db import transaction

#define DDFClient object to retrive DDF Data
ddf_c = DDFClient(MEDIA_DIR,format_type='STANDARD-XML',s3_reader=s3_reader)

#Starts an s3 session if S3 Reader is used
if s3_reader:
    s3_session = boto3.session.Session()

#writes records to DB. Passes ddf_clients listings data to the db_write.py module to write it to the db
def update_records(data):
    return db_write.update_records(data['Listings'])

#delete all db records
def erase_db():
    Property.objects.all().delete()
    DDF_LastUpdate.objects.all().delete()

#updates lastupdate time stamp in the database so the update can resume from this point in time during next update.
def write_last_update(last_update):
    try:
        last_update_obj,result = DDF_LastUpdate.objects.get_or_create(UpdateType='DDF')
        last_update_obj.LastUpdate=last_update
        last_update_obj.save()
        return True
    except Exception as e:
        logger.error(e)
        logger.error("Error updating last update value in DB")
        return False

#gets lastupdate time stamp from db
def read_last_update():
    logger.debug("Reading Timestamp")
    try:
        timestamp = DDF_LastUpdate.objects.get(UpdateType='DDF').LastUpdate
    except DDF_LastUpdate.DoesNotExist:
        logger.warning("adding initial timestamp")
        return None
    return timestamp

#deletes removed listings from db. removed_listings are identified by the ddf_client
def delete_records(removed_listings):
    try:
        count,deleted = Property.objects.filter(DDF_ID__in=removed_listings).delete()
        logger.info("Deleted %s old record from DB",count)
        return True
    except Exception as e:
        logger.error(e)
        logger.error("Error in Deleting old removed records")
        return False

#get lists of listing photos DIRs either locally or using S3 bucket
def get_current_photos_dirs(s3=None):
    dir =[]
    if s3:
        try:
            prefix = LISTING_DIR + '/' #needed for s3 code below to work
            FilesNotFound = True
            # source: https://stackoverflow.com/questions/35803027/retrieving-subfolders-names-in-s3-bucket-from-boto3
            #Paginator: https://www.slsmk.com/using-python-boto3-with-amazon-aws-s3-buckets/
            paginator = s3.get_paginator('list_objects')
            result = paginator.paginate(Bucket=AWS_STORAGE_BUCKET_NAME, Prefix=prefix, Delimiter='/')
            for pageobject in result:
                for o in pageobject.get('CommonPrefixes'):
                    dir.append(o.get('Prefix').strip(prefix).strip('/')) #beaware not to use Numbers in LISTING_DIR as a name. otherwise it will be stripped.
                    FilesNotFound = False
            if FilesNotFound:
               logger.error("Error or No Photos dir where found in S3 Bucket:%s",AWS_STORAGE_BUCKET_NAME)
        except Exception as e:
            logger.error(e)
            logger.error("Error occured white checking current DIRs in S3 Bucket: %s",AWS_STORAGE_BUCKET_NAME)
        logger.debug("Current DDF Photos DIRs:%s",dir)
        return dir

    else:
        try:
            dir =  next(os.walk(LISTING_DIR))[1]
        except Exception as e:
            ddf_c.media_handler.create_dir(LISTING_DIR)
            dir = next(os.walk(LISTING_DIR))[1]
    return dir

#retrive all photos info from the db for the purpose of comparasion against the new photo info from the ddf.
def get_photos_info():
    try:
        photos_info = {}
        for listing in Property.objects.all():
            if listing.ListingType == "DDF":
                #photos_info[listing.DDF_ID] = listing.Photos.values_list('SequenceId','LastUpdated')
                photos_info[listing.DDF_ID] = {}
                for photo in listing.Photos.all():
                    photos_info[listing.DDF_ID][str(photo.SequenceId)] = photo.LastUpdated
        return photos_info

    except Exception as e:
        logger.error(e)
        logger.error("Failed to get db photos info")
        return {}

#get list of photo files for a listing, used to sync photos.
def get_listing_photos_file_list(listing_id,s3=None):
    listing_dir_files = []
    if s3:
        try:
            prefix = LISTING_DIR + '/' +  listing_id  # needed for s3 code below to wkr
            FilesNotFound = True
            # source: https://stackoverflow.com/questions/35803027/retrieving-subfolders-names-in-s3-bucket-from-boto3
            #source: https://stackoverflow.com/questions/30249069/listing-contents-of-a-bucket-with-boto3
            paginator = s3.get_paginator("list_objects")
            page_iterator = paginator.paginate(Bucket=AWS_STORAGE_BUCKET_NAME, Prefix=prefix)
            for page in page_iterator:
                if "Contents" in page:
                    for key in page["Contents"]:
                        keyString = key["Key"]
                        FilesNotFound = False
                        listing_dir_files.append(keyString.split("/")[-1])
            if FilesNotFound:
                logger.error("No Photos found for listing:%s dir where found in S3 Bucket:%s",listing_id, AWS_STORAGE_BUCKET_NAME)
        except Exception as e:
            logger.error(e)
            logger.error("Error occured white checking listing id: %s Photos in S3 Bucket: %s", listing_id, AWS_STORAGE_BUCKET_NAME)
    else:
        try:
            listing_dir_path= LISTING_DIR + '/' + listing_id
            listing_dir_files = next(os.walk(listing_dir_path))[2]
            return listing_dir_files
        except Exception as e:
            logger.error(e)
    return listing_dir_files

#returns current listings IDs in db
def get_db_listing_ids():
    return list(Property.objects.values_list('DDF_ID', flat=True).filter())

#remove deleted photos listings DIRs by comparing the existing DIRs againts records in the DB. Folders with no db record will be deleted.
#db records changes according to the ddf update where some records get removed from the MLS server due to expiry
def delete_removed_photos_dirs(current_photos_dir_ids):
    try:
        listings_ids = get_db_listing_ids() #get current listing IDs from DB
        #get listings that has folders but doesn't exists in DB
        remove_photos_dir =[listing for listing in current_photos_dir_ids if listing not in listings_ids]
        logger.info("Total Listings %s, Total Photos DIR %s, DIR Photos to be removed %s",len(listings_ids),len(current_photos_dir_ids),len(remove_photos_dir))
        ddf_c.remove_old_listings_photos(remove_photos_dir) #remove deleted listings DIRs
        return True
    except Exception as e:
        logger.error(e)
        logger.error("Error in get_removed_photos_dirs")
        return False

#returns a list of agent photos in S3 or locally.
def get_agent_photos_list(s3=None):
    agent_photos=[]
    if s3:
        try:
            prefix = AGENTS_DIR + "/"  # needed for s3 code below to wkr
            FilesNotFound = True
            # source: https://stackoverflow.com/questions/35803027/retrieving-subfolders-names-in-s3-bucket-from-boto3
            #source: https://stackoverflow.com/questions/30249069/listing-contents-of-a-bucket-with-boto3
            paginator = s3.get_paginator("list_objects")
            page_iterator = paginator.paginate(Bucket=AWS_STORAGE_BUCKET_NAME, Prefix=prefix)
            for page in page_iterator:
                if "Contents" in page:
                    for key in page["Contents"]:
                        keyString = key["Key"]
                        FilesNotFound = False
                        agent_photos.append(keyString.split("/")[-1])
            if FilesNotFound:
                logger.error("No Agent Photos found for dir where found in S3 Bucket:%s",AWS_STORAGE_BUCKET_NAME)
        except Exception as e:
            logger.error(e)
            logger.error("Error occured white checking Agent Photos in S3 Bucket: %s", AWS_STORAGE_BUCKET_NAME)
    else:
        try:
            agent_photos = (os.walk(AGENTS_DIR))[2]
        except Exception as e:
            logger.error(e)
    return agent_photos

#sync_agent_photos: is for download agent photos
#Problem: Some agents do not have photos this function keep recognizing them as missing photos.
def sync_agents_photos(s3=None):
    try:
        agents_in_db = AgentDetails.objects.values_list('DDF_ID',flat=True).distinct() #get agents in db
        agents_in_dir = get_agent_photos_list(s3=s3)
        if not agents_in_dir:
            raise Exception("No Agent DIR Found or Failed to Read Data")
        missing_photos = [photo for photo in agents_in_db if str(photo)+".jpg" not in agents_in_dir]
        removed_photos = [photo_file for photo_file in agents_in_dir if photo_file.split('.')[0] not in agents_in_db ]
        for agent_photo_id in missing_photos: #if missing download --Removed as we don't have track of non available photos, this will cause delay each update.
           ddf_c.media_handler.get_agent_photo(agent_photo_id)
        # for photo_file in removed_photos: #if removed delete from files
        #     ddf_c.media_handler.delete_file(AGENTS_DIR + '/' + photo_file)
        logger.info("Agent Photos Sync was completed Successfully")
        return True
    except Exception as e:
        logger.error(e)
        logger.error("Error in Agents Photos Sync")
        return False


def sync_listing_photos(s3=None):
    #This function makes sures all the photos are synced correctly between the db records and the media files.
    #if db has records for photos that doesn't exists as a media file. These photos will be downloaded.
    #It also delete photos that doesn't have a record in the db
    try:
        current_photos_dir_ids = get_current_photos_dirs(s3=s3) #read current DIRs
        if not current_photos_dir_ids:
            raise Exception("Current Photos DIR are empty or failed to read from server, syncing was terminated")
        delete_removed_photos_dirs(current_photos_dir_ids) #delete removed Listing DIRs
        listings_objs = Property.objects.all() #get listings Objects
        for listing_obj in listings_objs:
            if listing_obj.Photos.exists(): #if listing Photos Tables exists
                if listing_obj.DDF_ID not in current_photos_dir_ids: #if DIR is missing
                    logger.info("Listing %s Photos weren't found in Media DIR",listing_obj.DDF_ID)
                    ddf_c.media_handler.create_photo_dir(listing_obj.DDF_ID) #create DIR for that listing
                    for photo_obj in listing_obj.Photos.all(): #Download all Photos
                        ddf_c.media_handler.get_photo(photo_obj.SequenceId,listing_obj.DDF_ID)
                else: #if DIR is not missing and listing Photos table exists, check photos individually
                    db_photos = list(listing_obj.Photos.values_list('SequenceId',flat=True).filter()) #list of Photos in db
                    dir_photos = get_listing_photos_file_list (listing_obj.DDF_ID,s3=s3) #photo files
                    missing_photos = [ photo for photo in db_photos if str(photo)+".jpg" not in dir_photos ] #missing photos
                    if missing_photos: #if photo is missing
                        logger.info("Detected Missing Photos :%s for Listing:%s",missing_photos,listing_obj.DDF_ID)
                        for missing_photo in missing_photos:
                            ddf_c.media_handler.get_photo(missing_photo, listing_obj.DDF_ID)
        logger.info("Photos Sync was completed Successfully")
        return True
    except Exception as e:
        logger.error(e)
        logger.error("Error in Listings Photos Sync")
        return False


#update_db: updated db from DDF then updates tables,
@transaction.atomic
def update_db(sample=False):
    #update_db is the primary function for reading the data from the DDF using the ddf_client and then updating the database accordingly.
    #It triggers the photos downloads according to the new records recevied from DDF.
    #if sample=True, only 10 records will be updated.
    try:
        skip_photos = False #Default to Download Photos
        previous_listings_keys = get_db_listing_ids() #current listings IDs
        last_update = read_last_update() #Last Update time Stamp
        if not last_update: #if no timestamp in the database
            add_initial_timestamp() #write an initial value
            last_update = DDF_LastUpdate.objects.get(UpdateType='DDF').LastUpdate #read it
            skip_photos = True #skip photos, will rely on the syncing

        new_last_update = ddf_c.get_gmt_time() #get new time stamp
        previous_photos = get_photos_info()
        if sample :
            updated = ddf_c.update(last_update=last_update, previous_listings_keys=previous_listings_keys,
                                ignore_restrictions=True,limit=10, previous_photos=previous_photos)
        else:
            updated = ddf_c.update(last_update=last_update, previous_listings_keys=previous_listings_keys,
                                ignore_restrictions=True, previous_photos=previous_photos,skip_photos=skip_photos)

        if not updated['Pass']: #if update failed by DDF client
        #if not updated['Status']:
            raise Exception("Failed to update DDF")
        else: #if update passed by DDF client
            if not update_records(updated): #if failed to write to db
                raise Exception("Failed to update new records to db")
            if not delete_records(updated['Removed_Listings']): #if failed to delete removed listings from db
                raise Exception("Failed to delete old records from db")
            if not write_last_update(new_last_update): #if failed to update timestamp
                raise Exception("Failed to update LastUpdate time stamp in db")
            logger.info("DB updated successfully") #updated successfully
        return True
    except Exception as e:
        logger.error(e)
        logger.error("Error in database update changes have been ignored")
        return False


def update_server(enable_photos_sync=True,sample=False):
    # update_server: is the parent function for updating the DDF records and photos.
    # It does the following
    # 1- Login
    # 2- calls update_db function to update DDF records and photos from the MLS server into the DB including the media files.
    # 3- applies photo_syncing to confirm all photos are synced and upto date.
    # 4- Logout.
    try:
        ddf_c.login()
        result = update_db(sample)
        if result:
            if enable_photos_sync and not sample:
                s3=None
                if s3_reader:
                    s3 = s3_session.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, #S3 has to be defined here otherwise, connection will drop.
                                           aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                sync_listing_photos(s3=s3)
                # sync_agents_photos(s3=s3) #Enable only at first Download. Causes Delays as it checks for Photos that doesn't exists.
        else:
            logger.info("Update Failed")
            ddf_c.logout()
            return False
        ddf_c.logout()
        logger.info("Server updated successfully")

    except Exception as e:
        logger.error(e)
        logger.error("Error in update_server")
        return False

#To initialize ddf_timestamp in the database.
def add_initial_timestamp():
    DDF_LastUpdate.objects.update_or_create(id=1, defaults={'LastUpdate': '2014-08-17T18:13:22Z', 'UpdateType': 'DDF'})

