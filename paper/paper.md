---
title: 'RETS-Manager: A production ready platform for fetching and syncing real estate data and images'
tags:
  - Python
  - Django
  - Real-Estate
  - RETS
  - Docker
  - Celery
authors:
  - name: Issam Hammad
    orcid: 0000-0000-0000-0000
    affiliation: 1
  - name: Kamal El-Sankary
    orcid: 0000-0000-0000-0000
    affiliation: 1
affiliations:
 - name: Electrical and Computer Engineering Department, Halifax, NS, Canada.
   index: 1
date: 21 June 2019
bibliography: paper.bib
---

# Summary

RETS-Manager is a Django based platform for retrieving, storing, and syncing real-estate data and images from multiple listing service (MLS) servers. This platform was designed based on the Canadian Real Estate Association (CREA) Data Distribution Facility (DDF®) payload structure and can be easily modified to support any other MLS server. The platform converts the raw XML data of the MLS servers to a structure data in a PostgreSQL or SQLite database. It also supports storing media files either locally or on AWS S3 bucket. Additionally, the platform is ready for deployment as a Docker Container and it supports automation scheduled updates using Redis and Celery.    This end-to-end solution for real-estate data can be used by researchers to obtain a clean structured data for research related to housing prices trends, predictions and statistics. Also, it can be used as a backend for real-estate websites. The platform was tested using tens-of-thousands of real live data.


# Motivation and Significance in Research

Studying real-estate market trends is extremely popular. Real-estate market health has a significant impact on the economy, therefore, analyzing up-to-date real-estate data is vital and is performed by different agencies and parties. Several open-source databases were proposed for real-estate data such as [@yehDataset:2018] which was proposed by [@yeh2018building] and the dataset [@mohDataset:2018] which was proposed by [@rafiei2015novel]. Several Machine Learning papers have used the datasets [@yehDataset:2018] and [@rafiei2015novel] even though they are relatively small where they contain 412 and 372 instances, respectively. Using small open-source datasets can be a major disadvantage especially for image-based machine learning research. The idea of building image-based machine learning solution for housing appraisal is a new idea that has been proposed in the literature. Examples can be seen in [@you2017image] and [poursaeed2018vision]. In North America, real-estate transactional data is stored on multiple listing service (MLS) servers owned by different regional real-estate associations. The data is stored using an XML unified format knows as Real Estate Transaction Standard (RETS) [@RETS_STANDARD:2006]. Accessing MLS data requires an API key which is usually given to licensed realtors or organizations.  Converting the RETS XML data to structured data and confirming that all the transactions are synced correctly can be a daunting task. This proposed platform provides an end-to-end solution where researchers can retrieve all the transactional data into a clean structure dataset and the images into structured folders either locally or on the cloud. Therefore, researchers can build clean datasets which can include up to hundreds of thousands of transactional data and images that are ready to be utilized in research given they have the needed API key.  


# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this: ![Example figure.](figure.png)

# Acknowledgements

We acknowledge contributions from Brigitta Sipocz, Syrtis Major, and Semyeong
Oh, and support from Kathryn Johnston during the genesis of this project.

# References
