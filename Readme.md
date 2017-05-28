

# Ride Sharing Project

The main aim of this project is to combine Individual trips to shared trips to reduce total distance travelled by taxies and to reduce the number of trips. To achieve this we have used k-means clustering and some Trip matching techniques with passenger count and delay time constraints. We also evaluated distance saved and number of trips saved before and after ridesharing.

## Installation Process

* Tested our approach with New york city real time data. You can download the dataset from the link below. (dataset - https://uofi.app.box.com/NYCtaxidata/2/2332219935 )

Below are the steps to run the code :

* Install python in your system (2.6 or above)
* Install mysql database and install package mysql.connector to connect to MySQL database from python
* Install GraphHopper to calculate the distance and time between two destination requests.
* To install Graphhopper API and build the function to calculate the distance and time between two points :
    * The New York OSM file can be obtained from: http://download.geofabrik.de/north-america/us/new-york.html 
    * Install the latest JRE and get GraphHopper Server as zip (~9MB)
    * Upzip the GraphHopper file and put the OSM file in the same dictionary. 
    * Run the command from window cmd under the dictionary: java -jar graphhopper-web-0.6.0-with-dep.jar jetty.resourcebase=webapp config=config-example.properties osmreader.osm=new-york-latest.osm.pbf
    * Please note that Graphhopper must be running all the time while algorithm is running.
	
## Run
Run the rideshare python file from the repositories using whichever python IDE you are working on.

## Reference 

https://www.packtpub.com/books/content/working-data-%E2%80%93-exploratory-data-analysis
https://en.wikipedia.org/wiki/K-means_clustering
https://en.wikipedia.org/wiki/GraphHopper
https://github.com/kkvamsi/NewYork-Taxi-Ridesharing
http://download.geofabrik.de/north-america/us/new-york.html
https://github.com/graphhopper/graphhopper/blob/0.6/docs/core/quickstart-from-source.md

## Team Members

* Nivetha Shanmuga Sundaram
* Upasna Menon
* Rashmitha Mary Allam
* Yang Hao

