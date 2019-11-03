-------------------------------------------------------------------------------------------------------------------------------
RETS MANAGER - Developed by: Issam Hammad
-------------------------------------------------------------------------------------------------------------------------------
Paper & Citation
-------------------------------------------------------------------------------------------------------------------------------
For academic use of this code. Please use the following citation

Hammad, Issam, Kamal El-Sankary, and Holly Hornibrook. "RETSManager: Real-estate database builder and synchronizer." SoftwareX 10 (2019): 100351.

Please also refer to the following paper for details about this repository.

https://www.sciencedirect.com/science/article/pii/S235271101930250X

Introduction
-------------------------------------------------------------------------------------------------------------------------------
RETS_Manager is a production ready framework for reading, storing and syncing real-estate data including images.

With the help of a real-estate agent, this framework was built based on the Data Distribution Facility (DDF®) data structure which was created by the Canadian Real Estate Association (CREA). Reading, deleting and modifying thousands of transactional data and images were tested.

This framework can read raw RETS data in XML format and store them in a PostgreSQL or SQLite database. It also provides a full syncing ability were the database will be updated automatically in terms of deleting and modifying records.
For Media, the framework provides the ability to store the images on AWS S3 or locally. Image syncing abilities is also provided.

Additionally, geocoding support is provided to store the lng/lat of the addresses.

The framework is Django ready. A web interface can be easily attached to this framework to have a fully functional website.
It can be also used by researchers to fetch real-estate data and images directly into a database.

For RETS requests. The framework used a local modified copy of an open-source RETS client library (rets_lib):
https://github.com/refindlyllc/rets

DDF documenation from CREA can be found under:
https://www.crea.ca/wp-content/uploads/2016/02/Data_Distribution_Facility_Data_Feed_Technical_Documentation.pdf

-------------------------------------------------------------------------------------------------------------------------------
RETS server setup
-----------------------------------------------------------------------------------------------------------------------------
If you are using the Canadian DDF, this framework is ready for deployment.

The framework uses the sample username and password provided by CREA for testing.

To access the actual MLS data you will require permission from CREA or you will need to be a CREA member (Real-Estate Agent)

Just go to ddf_manager/settings.py and enter your credentials (username and password)
Make sure the login_url is pointing to 'http://data.crea.ca/Login.svc/Login'

For data from other RETS server. Some code modifications will be required.
The web_app/models.py file has to be modified according to the structure of your RETS server.
Also, the ddf_manager/db_mapping.py file has to be adjusted.
Other changes in the ddf_manager might be required.

-------------------------------------------------------------------------------------------------------------------------------
Enabling S3
------------------------------------------------------------------------------------------------------------------------------
To enable S3 for images go to ddf_manager/aws_settings.py and enter your AWS info.
Also, make sure that S3 is enabled under ddf_manager/setting.py by setting 's3_reader = True'

-------------------------------------------------------------------------------------------------------------------------------
Local Media Storage
------------------------------------------------------------------------------------------------------------------------------
For local media storage make sure s3 is disabled 's3_reader = False'
Set the Media URL under ddf_manager/setting.py 'MEDIA_DIR'

-------------------------------------------------------------------------------------------------------------------------------
Logging
-------------------------------------------------------------------------------------------------------------------------------
Detailed logging for the updates will be recorded under ddf_client.log

-------------------------------------------------------------------------------------------------------------------------------
Project Structure
-------------------------------------------------------------------------------------------------------------------------------

First: /ddf_manager
This app contains the following two folder and files:

    1.    /rets_lib/: a modified version of the tiny RETS reader from https://github.com/refindlyllc/rets/tree/master/rets
    2.    /ddf_client/*: Is the core ddf reader, it uses rets_lib to read the data from the RETS server, it has the following files:

        a-    ddf_streamer.py: responsible for reading the transactional data from the RETS server. This includes retrieving the master-list for the ids of all the listings, reading listings since a specific time_stamp, and retirive specific listing by id.
        b-    ddf_s3.py: responsible for downloading images from DDF and save them to S3
        c-    ddf_media.py: responsible for downloading images from DDF and save them locally.
        d-    ddf_client.py, defines streamer and s3 classes to complete the data fetching.

    3.    Manager.py: Connects the Django models and the media storage to the ddf_client. Manages all data and images syncing.

    4.    db_write.py: Is a file used by manager.py to interface with Django Model.

    5.    db_mapping.py: Is a file used by db_write to map the Python Dictionaries retrieved using the DDF Client to the appropriate fields in DB.

    6.    db_summary.py: Used to add geolocation and other additional data.

    7.    ddf.py: Used by Celery for running the DDF Read.

    8.    ddf_logger.py: Logging settings.

    9.    Settings.py: Contains DDF app settings.

Second: /web_app

This folder contains an initial Django app that can be expanded to a full web interface.

The app contains the models as per the CREA DDF structure under models.py.

-------------------------------------------------------------------------------------------------------------------------------
Operating Modes
-------------------------------------------------------------------------------------------------------------------------------
This framework can be used in two modes:


#1- By local deployment as Django app (For manual selective data fetching).

    Simply use the project files as a Django app after installing all the requirements (requirements.txt).
    Good for research use where automatic updates are not required.

#2- Fully automated updates using a combination of Docker-Compose + Redis + Celery + Nginx. This enables automatic periodic updates.

    Make sure to enable DOCKER=True under RETS_Manager/settings.py. This will switch the database from SQLite to PostgreSQL

    Goto ddf_manager/ddf.py modify the settings of the celery worker including the update frequency

    Good for production enviroment where automatic updates for the database and the images are required.

    Can be converted to fully functioning real-estate website by just building a web_interface using the web_app.

    This was tested using Digital Ocean Docker instance.
    https://marketplace.digitalocean.com/apps/docker

Please refer to the next section for details about both modes.

-------------------------------------------------------------------------------------------------------------------------------
Local Installation
-------------------------------------------------------------------------------------------------------------------------------
This mode is for manual data retrieval. It uses the Django web server to retrieve data from the DDF into SQLite Database.
Both S3 or Local Media storage can work under this mode.

The following steps describe details on how to run this platform.
The steps below are tested using Windows:

    1- Start by creating your own virtual environment
        (Tested with python 3.5.4)
        $py -m venv rets

    2- Activate the virtual environment
        $cd rets
        $Scripts\activate

    3- clone this repo
        *if you don't have git -- please install (https://git-scm.com/download/win).
        $git clone https://github.com/issamhammad/RETSManager

    4- Install Requirements
        $cd RETSMANAGER
        $pip install -r requirements.txt
    5- Make Django migrations to web_app
        $py manage.py makemigrations web_app
    6- Apply Migrations
        $py manage.py migrate
    7- Startserver 
        *Select a [port]
        $py manage.py runserver [port]
    8- Using google chrome go to:
        http://127.0.0.1:[port]/

    9- If the documentation was loaded then the deployment was successful.

    10- Try a sample update using http://127.0.0.1:[port]/test/
        *You have to refresh the browser twice at least for the initial deployment. The first attempt will initialize the timestamp.
        **This step will use a sample free username/password by CREA to download sample data and images.
        ***Wait until the log file output appears on the browser before initiating the second refresh.

    11- Note that CREA server for samples login is glitchy. So you might have to refresh the page more than once to get results.
        *You might get this error "RETS Server Failure, Returned Code: 20701, Message: Not Logged In"

    12- If the update is successful the log file will show "Server updated successfully". 
    Note that the log file records all attempts. Confirm that you are looking at the right attempted data based on the time.

    13- If the update was successful you will find a newly created folder [media] in your root DIR

    14- You can use any SQLite browser to check the data in your DB. The database file is created under the root DIR.

-------------------------------------------------------------------------------------------------------------------------------
Docker Installation: (For full automation Docker + Redis + Celery + Nginx)
-------------------------------------------------------------------------------------------------------------------------------

This enables fully automated periodic updates using a combination of Docker-Compose + Redis + Celery + Nginx.

This mode is production ready and a web-interface can be integrated with it by modifying the web_app to have a fully functioning web site

The steps in this section were tested using Digital Ocean Docker Instance (Ubuntu 18.04)
https://marketplace.digitalocean.com/apps/docker
For other platforms installing docker and docker-compose is a prerequisite.

    1- Create this Digital Ocean Instance and log in using ssh.

    2- Clone the repo using '$git clone https://github.com/issamhammad/RETSManager'

    3- $cd RETSManager

    4- Edit RETS_Manager/setting.py to enable DOCKER=TRUE 
    (This will enable PostgreSQL database which is used via a docker-container rather than the local SQLite)

    5- [Optional]: Adjust update period by modifying ddf_manager/ddf.py

    6- Build the docker-container using '$docker-compose build'

    7- Start all containers using '$docker-compose up'
       **Due to containers dependencies some errors will appear initially but then everything gets resolved automatically.

    8- Confirm everything is working by going to <instance_ip>

    9- If the documentation loads then everything should be working.

    10- Following an update media files will be found under /media/
