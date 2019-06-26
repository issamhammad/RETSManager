---
title: 'RETS-Manager: A platform for fetching and syncing real estate data and images'
tags:
  - Python
  - Django
  - Real-Estate
  - RETS
  - Docker
  - Celery
authors:
  - name: Issam Hammad
    orcid: 0000-0002-1895-3438
    affiliation: 1
  - name: Kamal El-Sankary
    orcid: 0000-0001-8104-6913
    affiliation: 1
affiliations:
 - name: Electrical and Computer Engineering Department, Halifax, NS, Canada.
   index: 1
date: 21 June 2019
bibliography: paper.bib
---

# Summary

'RETS-Manager' is a Django based platform for retrieving, storing, and syncing real-estate data and images from multiple listing service (MLS) servers. This platform was designed based on the Canadian Real Estate Association (CREA) Data Distribution Facility (DDF) payload structure and can be easily modified to support any other MLS server. The platform converts and syncs the raw XML data originating from the MLS servers to a structure data in a PostgreSQL or SQLite database. It also supports storing media files either locally or on AWS S3 bucket. Additionally, the platform is ready for deployment as a Docker Container and it supports automated periodic updates using Redis and Celery. This end-to-end solution for real-estate data can be used by researchers to create a clean structured database with media files for research related to housing price trends, machine learning, market prediction, and statistics. Also, the platform can be converted to a real estate web application with a live feed by just adding a web interface. The platform was tested using tens-of-thousands of live real-estate data.


# Motivation and Significance in Research

Studying real-estate market trends is extremely popular. Real-estate market health has a significant impact on the economy, therefore, analyzing up-to-date real-estate data is vital and is performed by different agencies and parties. Several open-source databases were proposed for real-estate data such as [@yehDataset:2018] which was proposed by [@yeh2018building] and the dataset [@mohDataset:2018] which was proposed by [@rafiei2015novel]. Several machine learning papers have used the datasets [@yehDataset:2018] and [@rafiei2015novel] even though they are relatively small as they contain 412 and 372 instances, respectively. Using a small open-source dataset can be a major disadvantage in machine-learning especially for image-based machine learning research. The idea of building an image-based machine learning solution for home appraisal is a new idea that has been proposed in the literature. Examples can be seen in [@you2017image] and [poursaeed2018vision]. In North America, real-estate transactional data is stored on MLS servers owned by different regional real estate associations. The data is stored using an XML unified format known as Real Estate Transaction Standard (RETS) [@RETS_STANDARD:2006]. Converting the RETS XML data to structured data and confirming that all the transactions are synced and are up-to-date can be a daunting task. This proposed platform provides an end-to-end solution where researchers can retrieve the required transactional data into a clean structure dataset and the images into structured folders either locally or on the cloud. Therefore, researchers can build clean datasets which can include up to hundreds of thousands of transactional data and images that are ready to be utilized in research given they have access to an MLS server.

# Platform Structure

The platform was constructed based on CREA DDF's payload structure which is described in [@crea]. Therefore, it can be used without any modifications in order to build a dataset for the purpose of conducting research based on the Canadian housing market data. Additionally, with minor alterations to the database structure, the platform can support any MLS server worldwide. Testing was conducted using live data by obtaining an API key through collaborating with a real-estate agent. The platform consists of multiple hierarchical models which convert the raw XML data obtained from the MLS server to a fully synced structured database with synced images. Figure 1 illustrates the architecture of this platform. The 'ddf_client' application is responsible for updating and syncing listing data and images from the MLS server using the RETS client [@refindlyllc]. A local copy of [@refindlyllc] was included and slightly modified under the folder 'rets_lib'. The remaining modules of the platfom were natively developed.  To follow [@crea] guidelines, the 'ddf_client' starts by downloading all active records since the last download based on a timestamp. Then it requests a master-list of all the available listing IDs. Finally, it downloads the missing listings through 'request by ID' after comparing the database listings plus the received active listings against the master-list. The 'ddf_client' also downloads and syncs all the photos and identifies the expired listings that should be removed since the last timestamp. The DDF API [@crea] can return up to 100 listings per call. The client also handles this issue by sending multiple requests in sequence in order to download all the available records. The returned value of the 'ddf_client' is a python dictionary which contains full details regarding the new listings and the IDs of the removed listings since the last update. The 'ddf_manager' is another higher level application which employs and configures the 'ddf_client' in order to store the listings data into a database defined using a Django model. The 'ddf_manager' updates and syncs the database according to the data returned by the 'ddf_client'. The 'ddf_client' can be used as a stand-alone application without the 'ddf_manager' if storing the data into a synced database is not required. 'web_app' is a template for a Django web application which is used to define CREA's model. 'web_app' can be developed further by any user to add an interface to this platform by adding Django views and templates. 

![Platform Architecture.](Figure.png)

# Deployment Options

Two deployment options are available for this platform. The first is a production-ready solution for periodic updates which uses Docker-Compose along with Celery, Redis and Nginx. The second option is a simpler one which uses Django's web server excluding Celery or Docker. The second deployment option is perfect for researchers who just want to retrieve a few batches of data manually. Both deployment options are explained in details in the repository's documentation.

# References
