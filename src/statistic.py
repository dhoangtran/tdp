import numpy
import math
import time
import datetime
import googlemaps
import matplotlib.pyplot as plt

import settings

def getBoundingArea():
    
    fr = open(settings.dataFile)
    fw = open(settings.statFile, 'w')
    
    # skip first line
    fr.readline()
    nTripInCenter = 0;
    nTotalTrip = 0;
    
    max_longitude = - float('inf')
    min_longitude = float('inf')
    max_latitude = - float('inf')
    min_latitude = float('inf')
    for line in fr:
        #line = fr.readline()
        array = line.split(',')
        pickup_longitude = float(array[10])
        pickup_latitude = float(array[11])
        dropoff_longitude = float(array[12])
        dropoff_latitude = float(array[13])
        
        if (pickup_longitude < min_longitude): min_longitude = pickup_longitude
        if (pickup_longitude > max_longitude): max_longitude = pickup_longitude
        if (pickup_latitude < min_latitude): min_latitude = pickup_latitude
        if (pickup_latitude > max_latitude): max_latitude = pickup_latitude

    # print bounding area
    fw.write('Pickup bounding area: ' + str(min_longitude) + ',' + str(min_latitude) + ' ' + str(max_longitude) + ',' + str(max_latitude))
        
    fw.close()
    fr.close()        

def getBoundingArea2():
    
    fr = open(settings.dataFile)
    
    # skip first line
    fr.readline()
    nTripInCenter = 0;
    nTotalTrip = 0;
    
    max_longitude = - 73.732160
    min_longitude = - 74.243821
    max_latitude = 40.928536
    min_latitude = 40.496351
    long = []
    lat = []
    for line in fr:
        #line = fr.readline()
        array = line.split(',')
        pickup_longitude = float(array[10])
        pickup_latitude = float(array[11])
        dropoff_longitude = float(array[12])
        dropoff_latitude = float(array[13])
        long.append(pickup_longitude)
        lat.append(pickup_latitude)
    # print bounding area
    fr.close()
    
    return (long, lat)        
    
def getStatistic(sin, cos, ratio, deltaX, deltaY, nRow, nCol, originPosition, nRegions):
    
    fr = open(settings.dataFile)
    fw = open(settings.statFile, 'w')
    # skip first line
    fr.readline()
    nTripInCenter = 0;
    nTotalTrip = 0;

    for line in fr:
        #line = fr.readline()
        array = line.split(',')
        pickup = [float(array[10]), float(array[11])]
        dropoff = [float(array[12]), float(array[13])]
        pickup1 = getPositionToPoint(sin, cos, ratio, originPosition, pickup)
        dropoff1 = getPositionToPoint(sin, cos, ratio, originPosition, dropoff)
        pickupRegion = getRegion(deltaX, deltaY, nRow, nCol, pickup1)
        dropoffRegion = getRegion(deltaX, deltaY, nRow, nCol, dropoff1)

        nTotalTrip += 1         
        if (pickupRegion > -1 and dropoffRegion > -1):
            nTripInCenter += 1

    # print last demand
    fw.write('Number of trips in Center ')
    fw.write(str(nTripInCenter))
    fw.write('Total number of trips ')
    fw.write(str(nTotalTrip))
    
    fw.close()
    fr.close()

def scatterplot(x_data, y_data, x_label="", y_label="", title="", color = "r", yscale_log=False):

    # Create the plot object
    _, ax = plt.subplots()

    # Plot the data, set the size (s), color and transparency (alpha)
    # of the points
    ax.scatter(x_data, y_data, s = 10, color = color, alpha = 0.75)

    if yscale_log == True:
        ax.set_yscale('log')

    # Label the axes and provide a title
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    
    plt.show()


(long, lat) = getBoundingArea2()
scatterplot(long, lat)
