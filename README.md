# Green in the city
In this repository you'll find all the tools needed to prepare data for the Green in the City project. 

## Contents
This repository consists of 2 parts. 
### 1. Workshop
The first part contains the prepared data for the 'green in the city' demo workshop for the citie of Atlanta. The 'Workshop' folder contains this part. Since only data files are included in this folder, it is not uploaded to Github, but has to be downloaded using this link: https://ugentbe-my.sharepoint.com/:f:/g/personal/sander_taragola_ugent_be/Ei5-d6ZwJWJEjBMa-on7oIoBh8cy2WcYSUXFWO57e3KARQ?e=KOqNZE

### 2. Data Preparation
The second part contains all information and data related to data preparation. This can be found in the Data Preparation folder.  This folder is divided into satellite image processing, census data preparation, and raw data for both satellite imagery and census data.
#### **Satellite Images**.
Here you will find the scripts for downloading the Sentinel-2 images using Google Earth Engine, and a QGIS model for processing the satellite images and combining them with the geographic census data. The 'Demo' folder contains a sample script for both exploring and downloading the Sentinel-2 data. The 'Explore' and 'Download' folders contain scripts for exploring and downloading the images, respectively, resulting in the raw data (see below).
#### **Census Data**.
The census data folder contains the Python scripts and notebooks used to process the data. However, some functions used in data preprocessing are stored in the package "censusclean", which can be found in the root folder of this repository. 
#### **Raw Data**.
The raw data folder contains all the data preprocessing files used for the demo version. All preprocessing scripts are also linked to this folder, but the folder cannot be found on Github because it contains more than 100 Mb of data. The folder can be found using the following link: https://ugentbe-my.sharepoint.com/:f:/g/personal/sander_taragola_ugent_be/EsSkzc6NjatDpuywZlpSnxcBn2gixzF7aMErEwsUAVFeQg?e=xC2vzY

In order for the Python scripts to work, the directory must be downloaded to the following location
'green_in_the_city\data_preparation\'.