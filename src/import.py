import numpy
import math
import time
import datetime
import googlemaps

import settings

def getPositionDistance(ratio, position1, position2):
    return ((position1[0] - position2[0]) ** 2 + ((position1[1] - position2[1])*ratio) ** 2) ** 0.5

def getPointDistance(point1, point2):
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

def getGeoDistance(position1, position2):
    gmaps = googlemaps.Client(key='AIzaSyCG8siA4X6ec5rOTbbiuDgdzbNpmAjsdsI')
    origins = [[position1[1], position1[0]]]
    destinations = [[position2[1], position2[0]]]
    matrix = gmaps.distance_matrix(origins, destinations, mode="driving", units="imperial")
    distance = round(int(matrix['rows'][0]['elements'][0]['distance']['value']) / 1609.34, 2)
    return distance

def getRegion(deltaX, deltaY, nRow, nCol, point):
    region = -1
    i = int(math.floor(point[1] / deltaY))
    j = int(math.floor(point[0] / deltaX))
    if (i >= 0 and i < nRow and j >= 0 and j < nCol):
        region = i * nCol + j
    return region

def getPositionToPoint(sin, cos, ratio, originPosition, position):
    temp = [0.0, 0.0]
    temp[0] = position[0] - originPosition[0] 
    temp[1] = (position[1] - originPosition[1]) * ratio
    point = [0.0, 0.0]
    point[0] = temp[0] * cos - temp[1] * sin
    point[1] = temp[0] * sin + temp[1] * cos
    return point

def getPointToPosition(sin, cos, ratio, originPosition, point):
    temp = [0.0, 0.0]
    temp[0] = point[0] * cos - point[1] * (-sin)
    temp[1] = (point[0] * (-sin) + point[1] * cos) / ratio
    position = [0.0, 0.0]
    position[0] = round(originPosition[0] + temp[0], 6)
    position[1] = round(originPosition[1] + temp[1], 6)
    return position

def getDistanceMatrix(sin, cos, ratio, nRegions, originPosition):
    
    f = open('C:/Users/r0660215/workspace/balancing/data/4x50_distance_matrix_2.txt', 'w')
    
    distances = numpy.zeros((nRegions, nRegions))
    for r1 in range(48, 50):
        for r2 in range(nRegions):
            time.sleep(1)
            print r1, r2
            i1 = r1 / nCol
            j1 = r1 % nCol
            i2 = r2 / nCol
            j2 = r2 % nCol
            point1 = [j1 * deltaX + deltaX / 2, i1 * deltaY + deltaY / 2]
            point2 = [j2 * deltaX + deltaX / 2, i2 * deltaY + deltaY / 2] 
            position1 = getPointToPosition(sin, cos, ratio, originPosition, point1)
            position2 = getPointToPosition(sin, cos, ratio, originPosition, point2) 
            distances[r1, r2] = getGeoDistance(position1, position2)
            f.write(str(distances[r1,r2]))
            f.write(" ")
        f.write("\n")
    
    f.close()
    #return distances
 
def getMobilityPattern(sin, cos, ratio, deltaX, deltaY, nRow, nCol, originPosition, nRegions):
    f = open('C:/Users/r0660215/data/FOIL2010/trip_data_1.csv')
    mobilityPattern = numpy.zeros((nRegions, nRegions))
    totalPickup = numpy.zeros(nRegions)
    # skip first line
    f.readline()
    for line in f:
        #line = f.readline()
        array = line.split(',')
        pickup = [float(array[10]), float(array[11])]
        dropoff = [float(array[12]), float(array[13])]
        pickup1 = getPositionToPoint(sin, cos, ratio, originPosition, pickup)
        dropoff1 = getPositionToPoint(sin, cos, ratio, originPosition, dropoff)
        pickupRegion = getRegion(deltaX, deltaY, nRow, nCol, pickup1)
        dropoffRegion = getRegion(deltaX, deltaY, nRow, nCol, dropoff1)
        if (pickupRegion > -1 and dropoffRegion > -1):
            totalPickup[pickupRegion] += 1
            mobilityPattern[pickupRegion, dropoffRegion] += 1
    f.close()

    for i in range(nRegions):
        if totalPickup[i] > 0:
            for j in range(nRegions):
                mobilityPattern[i, j] = mobilityPattern[i, j] * 1.0 / totalPickup[i]
        else:
            mobilityPattern[i, i] = 1
            
    f = open('C:/Users/r0660215/workspace/balancing/data/4x50_mobility_pattern.txt', 'w')    
    for i in range(nRegions):
        for j in range(nRegions):
            f.write(str(mobilityPattern[i, j]))
            f.write(' ')
        f.write('\n')
    f.close()

def getInitialSupply(sin, cos, ratio, deltaX, deltaY, nRow, nCol, originPosition, nRegions):

    nTaxi = 13341
    fr = open('C:/Users/r0660215/data/FOIL2010/trip_data_1.csv')
    # skip first line
    fr.readline()
    taxiLocation = numpy.full((31, 24, nTaxi), -1)    
    for line in fr:
    #for i in range(100000):
        #line = fr.readline()
        array = line.split(',')
        taxiId = int(array[0]) - 2010000001
        #pickup_datetime = datetime.datetime.strptime(array[5], '%Y-%m-%d %H:%M:%S')
        dropoff_datetime = datetime.datetime.strptime(array[6], '%Y-%m-%d %H:%M:%S')
        day = dropoff_datetime.day - 1
        hour = dropoff_datetime.hour
        pickup = [float(array[10]), float(array[11])]
        dropoff = [float(array[12]), float(array[13])]
        pickup1 = getPositionToPoint(sin, cos, ratio, originPosition, pickup)
        dropoff1 = getPositionToPoint(sin, cos, ratio, originPosition, dropoff)
        pickupRegion = getRegion(deltaX, deltaY, nRow, nCol, pickup1)
        dropoffRegion = getRegion(deltaX, deltaY, nRow, nCol, dropoff1)        
        if pickupRegion > -1 and dropoffRegion > -1:
            taxiLocation[day, hour, taxiId] = dropoffRegion
    fr.close()
    
    # print supply
    fw = open('C:/Users/r0660215/workspace/balancing/data/4x50_initial_supply.txt', 'w')
    date = datetime.datetime.strptime('2010-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    for d in range(31):
        for h in range(24):
            fw.write(str(date.date()))
            fw.write(', ')
            fw.write(str(h))
            fw.write(', ')
            regionSupply = numpy.zeros(nRegions)
            for i in range(nTaxi):
                if taxiLocation[d, h, i] > -1:
                    regionSupply[taxiLocation[d, h, i]] += 1
            for j in range(nRegions):
                fw.write(str(int(regionSupply[j])))
                fw.write(' ')
            print numpy.sum(regionSupply)
            fw.write('\n')
        date += datetime.timedelta(days=1)
    fw.close()
    

def getPredictedDemand(sin, cos, ratio, deltaX, deltaY, nRow, nCol, originPosition, nRegions):

    origin_datetime = datetime.datetime.strptime('2010-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')    
    fr = open('C:/Users/r0660215/data/FOIL2010/trip_data_1.csv')
    fw = open('C:/Users/r0660215/workspace/balancing/data/4x50_predicted_demand.txt', 'w')
    # skip first line
    fr.readline()
    origin_datetime = datetime.datetime.strptime('2010-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    temp = origin_datetime
    regionDemand = numpy.zeros(nRegions)

    for line in fr:
        #line = fr.readline()
        array = line.split(',')
        pickup_datetime = datetime.datetime.strptime(array[5], '%Y-%m-%d %H:%M:%S')
        #dropoff_datetime = datetime.datetime.strptime(array[6], '%Y-%m-%d %H:%M:%S')
        pickup = [float(array[10]), float(array[11])]
        dropoff = [float(array[12]), float(array[13])]
        pickup1 = getPositionToPoint(sin, cos, ratio, originPosition, pickup)
        dropoff1 = getPositionToPoint(sin, cos, ratio, originPosition, dropoff)
        pickupRegion = getRegion(deltaX, deltaY, nRow, nCol, pickup1)
        dropoffRegion = getRegion(deltaX, deltaY, nRow, nCol, dropoff1)

        if temp.date() != pickup_datetime.date() or temp.hour != pickup_datetime.hour:
            # print old demand
            fw.write(str(temp.date()))
            fw.write(', ')
            fw.write(str(temp.hour))
            fw.write(', ')
            for j in range(nRegions):
                fw.write(str(int(regionDemand[j])))
                fw.write(' ')
            fw.write('\n')
            # new demand
            regionDemand = numpy.zeros(nRegions)
            temp = pickup_datetime
        
        if (pickupRegion > -1 and dropoffRegion > -1):
            regionDemand[pickupRegion] += 1

    # print last demand
    fw.write(str(temp.date()))
    fw.write(', ')
    fw.write(str(temp.hour))
    fw.write(', ')
    for j in range(nRegions):
        fw.write(str(int(regionDemand[j])))
        fw.write(' ')
    
    fw.close()
    fr.close()        

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
    
# main

p0 = [-74.040039, 40.710784]
p1 = [-73.992703, 40.690645]
p2 = [-73.914941, 40.797746]
p3 = [-73.962791, 40.817171]

ratio = 11.123 / 8.433
width = getPositionDistance(ratio, p0, p1)
height = getPositionDistance(ratio, p0, p3)
sin = (p3[0] - p0[0]) / height
cos = (p3[1] - p0[1]) * ratio / height
originPosition = p0
nRow = 10
nCol = 5
nRegions = nRow * nCol
deltaX = width / nCol
deltaY = height / nRow

# ---
#getDistanceMatrix(sin, cos, ratio, nRegions, originPosition)
#getMobilityPattern(sin, cos, ratio, deltaX, deltaY, nRow, nCol, originPosition, nRegions)   
#getPredictedDemand(sin, cos, ratio, deltaX, deltaY, nRow, nCol, originPosition, nRegions)
#getInitialSupply(sin, cos, ratio, deltaX, deltaY, nRow, nCol, originPosition, nRegions)
getStatistic(sin, cos, ratio, deltaX, deltaY, nRow, nCol, originPosition, nRegions)

