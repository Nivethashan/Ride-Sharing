import datetime
import json

import matplotlib.pyplot as plt
import mysql.connector
import numpy as np
import requests
from mysql.connector import errorcode
from scipy.cluster.vq import kmeans2, whiten

from Rideshare import Timeframe


# Since downloaded dataset is in .csv file, create a new table in mysql database with the same field names,
# and load all the data into the created table
# Our aim is to work with single source pickup (JFK), for that we filtered data with pickup location only
# as JFK within 2 mile radius
# The set of below commented code should be run only for the first time when you run the program.

# query = "CREATE TABLE trip_data_11(medallion VARCHAR(20),hack_license VARCHAR(20)," \
#         "vendor_id varchar(10),rate_code INT,store_and_fwd_flag varchar(5),pickup_datetime datetime" \
#         " , dropoff_datetime datetime,passenger_count INT,trip_time_in_secs INT," \
#         "trip_distance DOUBLE,pickup_longitude DECIMAL(20,10),pickup_latitude DECIMAL(20,10)," \
#         "dropoff_longitude DECIMAL(20,10),dropoff_latitude DECIMAL(20,10))"
# cursor.execute(query)

# load_query = "LOAD DATA LOCAL INFILE '/Users/Nivetha/Downloads/trip_data_8.csv' " \
#              "INTO TABLE tripdata FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 LINES"

# jfk_query = "CREATE TABLE jfk_data_12 AS SELECT *, ( 3959 * acos ( cos ( radians(40.645574) )" \
#             " * cos( radians( pickup_latitude ) ) * cos( radians( pickup_longitude ) - radians(-73.784866) )" \
#             " + sin ( radians(40.645574) ) * sin( radians( pickup_latitude ) ) ) ) " \
#             "AS distance FROM trip_data_12 HAVING distance < 2 and passenger_count<=4"
# cursor.execute(jfk_query)


# Implementation of K-means clustering and Trip Matching Algorithm

def kmeanscluster(starttime , endtime):
    global numpool

    # Connecting to MySQL Database where the database is stored using MySQL Connector package

    try:
        cnn = mysql.connector.connect(
            user='root',
            password='root',
            host='localhost',
            port=8889,
            database='test')
        # print("it works")
    except mysql.connector.Error as e:
        if e.errno == errorcode.ER_ACCESS_DENIED_CHANGE_USER_ERROR:
            print("somethind os wrong with username and password")
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            print("database doesn't exist")
        else:
            print(e)

    cursor = cnn.cursor()

    # This function is to select a particular pool's source and its destination points, Total
    # number of records and passenger count for each trip

    def selecteachpool():
        # This query is to select fields with filtering data for a particular pool.
        query = "Select medallion, dropoff_longitude, dropoff_latitude, passenger_count from jfk_data_12 WHERE pickup_datetime >= '" + str(starttime) + "'and pickup_datetime < '" + str(endtime) + "'"
        cursor.execute(query)
        result_set = cursor.fetchall()
        coord_list = []
        passenger_count = []
        for row in result_set:
            temp = [float(row[1]), float(row[2])]
            coord_list.append(temp)

        for row in result_set:
            passenger_count.append(int(row[3]))

        recordcount = 0
        for outerlist in coord_list:
            recordcount += 1
        return coord_list, passenger_count, recordcount

    # Returns the list of dropoff latitude and longitude points
    def getcoord_list():
        return coord_list

    # calculating value of k to run k-means clustering Algorithm
    def getkvalue(recordcount):
        kvalue = (int)(recordcount / 4)
        # print("No of records:", count)
        return kvalue

    # Run K-means clustering Algorithm using scipy-cluster package.
    def kmeanscluster(coord_list):
        coordinates = np.array(coord_list)
        return kmeans2(whiten(coordinates), kvalue, missing='warn',)

    # To plot the k-means clutering results in form of graph
    def plotkmeanscluster(coord_list, labels):
        coordinates = np.array(coord_list)
        plt.scatter(coordinates[:, 0], coordinates[:, 1], c=labels, iter = 5)
        plt.show()

    # To get the cluster points after running k-means clustering Algorithm
    def getclusterpoints(coord_list, labels, kvalue):
        clusterpt = [0 for x in range(kvalue)]
        for i in range(0, kvalue):
            clusterpt[i] = []
        listitem = 0
        for i in labels:
            clusterpt[i].append(coord_list[listitem])
            listitem = listitem + 1
        return clusterpt

    # Print those cluster points(dropoff latitudes and dropoff longitudes)
    def printclusterpoints(clusterpt, kvalue):
        print("\nkmeans clustering result \n")
        for i in range(0, kvalue):
            print("cluster number:", i, clusterpt[i])

    # After clustering is formed, merge trips with maximum capacity of 4
    def carassignment(clusterpt, kvalue):
        carassign = []
        carcount = -1
        for i in range(0, kvalue):
            for j in range(0, len(clusterpt[i])):
                if (j % 4 == 0):
                    carassign.append([])
                    carcount = carcount + 1
                    carassign[carcount].append(clusterpt[i][j])
                else:
                    carassign[carcount].append(clusterpt[i][j])
        return carassign, carcount + 1

    # Get the dropoff latitude and longitude points after we merged the trips
    def getcarassignment():
        return carassign, carcount

    # print trips after we merged the trips
    def printridesshared(carassign, carcount):
        print("\nRide shared cars and its destination\n")
        for i in range(0, carcount):
            print("car number:", i, carassign[i])

    coord_list, passenger_count, recordcount = selecteachpool()
    if (len(coord_list) < 4): # Skipping pools where the trips are too small or zero
        return
    kvalue = getkvalue(recordcount)
    meanpoints, labels = kmeanscluster(coord_list)
    # plotkmeanscluster(coord_list,labels)

    clusterpt = getclusterpoints(coord_list, labels, kvalue)
    # printclusterpoints(clusterpt, kvalue)
    carassign, carcount = carassignment(clusterpt, kvalue)
    # printridesshared(carassign, carcount)

    cnn.commit()
    cursor.close()
    cnn.close


    # To get distance and Time between two latitude and longitude points using graphhopper API

    def getDistance(plat,plong,dlat,dlong):
        requestString = 'http://localhost:8989/route?point=' + str(plat) + '%2C' + str(plong) + '&point=' + str(
            dlat) + '%2C' + str(dlong) + '&vehicle=car'
        r = requests.get(requestString)

        res = json.loads(r.text)

        return_list = []
        if ('paths' in res):
            return_list.append(res['paths'][0]['distance'])
            return_list.append(res['paths'][0]['time'])
            return return_list
        else:
            return_list.append(-250)
            return_list.append(-250)
            return return_list

    # To get the total travel distance before ridesharing
    def getwithoutridesharingdistance(coord_list):
        # Initialize some global and local variables
        global tnormaldist
        global wolength
        wolength = wolength + len(coord_list)
        normaldistance = 0
        # Calculate  distance between JFK and all the destination points
        for i in range(0, len(coord_list)):
            dist = getDistance(40.645574, -73.784866, coord_list[i][1], coord_list[i][0])
            normaldistance = normaldistance + dist[0]
        normaldistance = normaldistance/1000
        tnormaldist = tnormaldist + normaldistance # Sum up all the trip distances
        print("\nDistance without ride sharing:",normaldistance,"km")
        return normaldistance

    # To get the total travel distance After ridesharing
    def getwithridesharingdistance(carassign,carcount):
        # Initialize some global and local variables
        global tridesharedist
        global wlength
        wlength = wlength + len(carassign)
        ridesharedist = 0
        # Calculate  distance travelled by trips after ridesharing
        # For that, we took JFK as source and First destination point as destinaation
        # After first passenger dropped off, Keep Previous Destination point as source and current destination
        # point as destination and repeat the process till all the passengers for a trip dropped off.
        for i in range(0,carcount):
            initlat = 40.645574
            initlog = -73.784866
            for j in range (0,len(carassign[i])):
                if(j!=0):
                    initlat = carassign[i][j-1][1]
                    initlog = carassign[i][j-1][0]
                distance = getDistance(initlat, initlog, carassign[i][j][1], carassign[i][j][0])
                ridesharedist = ridesharedist + distance[0]

        ridesharedist = ridesharedist/1000
        tridesharedist = tridesharedist + ridesharedist # Sum up all the trip distances
        print("Distance with ride sharing:",ridesharedist,"km")
        return ridesharedist

    # This function returns the distance saved in percentage
    def getsaveddistance(normaldistance,ridesharedist):
        global totaldistance
        distancesaved = (1-(ridesharedist/normaldistance))*100
        totaldistance = totaldistance + distancesaved

    normaldistance = getwithoutridesharingdistance(coord_list)
    ridesharedist = getwithridesharingdistance(carassign, carcount)
    getsaveddistance(normaldistance, ridesharedist)
    numpool = numpool + 1 # To calculate the total number of pools


# Initializing some global variables

starttime = Timeframe.starttime
endtime = Timeframe.endtime
numpool = 0
totaldistance = 0
tnormaldist = 0
tridesharedist = 0
wolength = 0
wlength = 0

programstarttime = datetime.datetime.now() # Record the system time before start of the Algorithm
print("\nAlgorithm start time:",programstarttime)

# Run the Algorithm for each pool window until the end time.

while endtime <= Timeframe.untildatetime:
    print("\npool : ",starttime, "-",endtime)
    kmeanscluster(starttime,endtime)
    starttime = starttime + Timeframe.windowsize
    endtime = endtime + Timeframe.windowsize

programendtime = datetime.datetime.now() # Record the system time After end of the Algorithm
print("\nAlgorithm End time:",programendtime)

# Calculate the difference between start and the end time
timeobj = programendtime - programstarttime

print ("Total time to run the Algorithm:", timeobj)
print("Average run time for each pool:",timeobj/numpool)

print ("\nTotal distance without ridesharing:",tnormaldist,"km")
print ("Total distance with ridesharing:",tridesharedist,"km")

print("\nNumber of pools:",numpool)

print ("\nAverage distance without ridesharing for eachpool:",tnormaldist/numpool,"km")
print ("Average distance with ridesharing for each pool",tridesharedist/numpool,"km")

print ("\nAverage number of trips Before RideSharing:",wolength/numpool)
print ("Average number of trips After RideSharing:",wlength/numpool)

