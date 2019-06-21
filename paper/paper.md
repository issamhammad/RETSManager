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
    orcid: 0000-0003-0872-7098
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

RETS-Manager is a Django based platform retrieving for retrieving, storing, and syncing real-estate data and images from multiple listing service (MLS) servers. This platform was designed based on the Canadian Real Estate Association (CREA) Data Distribution Facility (DDF®) payload structure and can be easily modified to support any other MLS server. The platform converts the raw XML data of the MLS servers to a structure data in a PostgreSQL or SQLite database. It also supports storing media files either locally or on AWS S3 bucket. Additionally, the platform is ready for deployment as a Docker Container and it supports fully automation scheduled tasks using Redis and Celery.    This end-to-end solution for real-estate data can be used by researchers to obtain a clean structured data for research related to housing prices trends, predictions and statistics. Also, it can be used as a backend for real-estate websites

# Motivation and Research Significance

Studying real-estate market trends is extremely popular. Real-estate market health has a significant impact on the economy, therefore, analysing up-to-date real-estate data is vital and is performed by different agencies and parties. Several open-source databases were proposed for real-estate data such as [2] which was proposed by [3] and the dataset [4] which was proposed by [5]. Several Machine Learning papers have used the datasets [2] and [4] In North America, Real-estate data is stored on multiple listing service (MLS) servers owned by different regional associations. The data is stored using a unified format knows as Real Estate Transaction Standard (RETS) [1]. RETS is XML based, therefore all MLS Application programming interface (API) will return XML data. Converting this data to a structured data and confirming that all the transactions are synced correctly can be a daunting tasks. 


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
