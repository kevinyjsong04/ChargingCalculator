import pprint
from pip._vendor import requests
from dateutil import tz
import datetime
import json
import matplotlib.pyplot as plot
import matplotlib.colors as mcolors
import pytz


# import pandas as pd
# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

# Create a script that can gather irradiance data for the charging times
# and calculate ranges of minimum and maximum expected SOC increases during charging sessions.
# Output can be in the form of a bar graph. Stretch goal can be a Jupyter Notebook GUI that creates a JSON file of the parameters

# use ghi value, convert different time from timezones to EST

# after getting data from Solcast API through json file
# extract specifically the ghi values and put in a dict data structure
# key is related to ghi, value is the value, also get times and convert
# once all values are inside the dict, then use formula to calculate expected SOC increases

# convert to SOC expected increased -> energy / (4.7 x 1000) x 100 to get percentage increase

# have a UI that asks for time period and number of charging sessions -->
# give expected SOC percentage increases for each of the time periods

# This is our own class to add items to dictionary
class myDictionary(dict):

    def __init__(self):
        self = dict()

    def add(self, key, value):
        self[key] = value


# Our first function to gather irradiance values and match it with time.
def chargeSegment(latitude, longitude, date):
    soulcastAPI = "_3a3wT9RxwYesu6GW-ko4pmaAcxrqrW8"

    query = {
        "format": "json",
        "api_key": soulcastAPI,
        "Latitude": latitude,
        "Longitude": longitude,
        "hours": 48 #limiting solcast to feed data for next 48 hours
    }
    apiCall = requests.get("https://api.solcast.com.au/world_radiation/forecasts", params=query).json()
    #pprint.pprint(apiCall)

    irradianceList = []
    timeList = []

    # Gathering the irradiance from the JSON
    # for ghi in apiCall["forecasts"]:
    #    irradianceList.append(ghi["ghi"])


    '''take datetime and use to get the date - timing[:11]  and get the 12-20th indexes of timing or the time in hr:min:sec and -6'''
    for data in apiCall["forecasts"]:
        timing = data["period_end"]
        #print(timing)
        originalZone = tz.gettz("UTC")  # Original timezone in UTC
        newTimeZone = tz.gettz("America/Chicago")
        timing = timing[:18:] + timing[-1]
        utc = datetime.datetime.strptime(timing, "%Y-%m-%dT%H:%M:%SZ")
        utc.replace(tzinfo=originalZone)
        cst = utc.astimezone(tz=newTimeZone)
        #print(str(utc) + "|||||" + str(cst))
        cst = str(cst)
        utc = str(utc)
        timeList.append(cst[:16])  # '''
        irradianceList.append(data["ghi"])

    # print(irradianceList)
    # print(timeList)

    # As of right now, we are using SR3 values
    solarEfficiency = 0.80  # Value given from Bailey for SR3
    arrayArea = 4;  # in m^2 for SR3
    time = 0.5 #in hours

    # Makes the list of energy values in Wh
    energyList = []
    for i in range(0, len(irradianceList)):
        energy = irradianceList[i] * arrayArea * solarEfficiency * time
        energyList.append(energy)

    # Makes a list of energy percentage values
    energyPercentage = []
    for i in range(0, len(energyList)):
        energyPercent = float((energyList[i] / 4700.00) * 100)
        formattedPercentage = "{:.3f}".format(energyPercent)  # formatting to 3 decimal places
        energyPercentage.append(formattedPercentage)

    # Put these values in a dictionary
    timeEnergyPair = myDictionary()
    for i in range(0, len(timeList)):
        # timeEnergyPair.add(timeList[i], irradianceList[i])
        timeEnergyPair.add(timeList[i], energyPercentage[i])

    #pprint.pprint(timeEnergyPair)
    return timeEnergyPair





def generateGraphData(numOfSegments, start, end, energyData):

    # loop through each segment
    #separate the data for each segment
    #get into graph, example shown below:

    #x-Coordinate
    timePeriod = []
    #y-Coordinate -> in percentage
    totalExpectedCharge = []
    #color
    colors = []
    
    #could optimize this by splitting chargeSegment into smaller functions
    #get al the times
    timeList = list(energyData.keys())

    for i in range(0, numOfSegments):
        chargeIncrease = 0.0
        startTarget = start[i]
        endTarget = end[i]
        startIndex = list(energyData).index(startTarget)
        endIndex = list(energyData).index(endTarget)
        #we want the values at the end times, so ignore the first index
        for j in range(startIndex + 1, endIndex):
            chargeIncrease += float(energyData.get(timeList[j]))
        timePeriod.append(startTarget + "-" + endTarget)
        totalExpectedCharge.append(chargeIncrease)
        #colors.append('blue')
    cmap = plot.cm.get_cmap('RdYlGn')
    norm = mcolors.Normalize(min(totalExpectedCharge), max(totalExpectedCharge))
    colors = [cmap(norm(val)) for val in totalExpectedCharge]
    plot.bar(timePeriod, totalExpectedCharge, color = colors)
    plot.title('Total Expected SOC increase over time periods', fontsize=12)
    plot.xlabel('Time Segments', fontsize=12)
    plot.ylabel('Expected SOC increase in %', fontsize=12)
    plot.grid(True)
    plot.show()



# Asking for latitude and longitude
# testLatitude = 38.927142183
# testLongitude = -95.676805255


latitude = float(input("Enter latitude of location: "))
longitude = float(input("Enter longitude of location: "))
energyPercentDict = chargeSegment(latitude, longitude, [])  # Kansas
# chargeSegment(33.7490, -84.3880,[]) # Atlanta

numOfSegments = int(input("Enter the number of segments of charge: "))
 
startTime = []
endTime = []
for i in range(0, numOfSegments):
    startTime.append(str(input("Enter start time -> format example: xxxx-xx-xx xx:xx or 2022-09-29 08:00 -> ")))
    endTime.append(str(input("Enter end time(Make sure this is after the start time) -> format example: xxxx-xx-xx xx:xx or 2022-09-29 08:30 -> ")))

generateGraphData(numOfSegments, startTime, endTime, energyPercentDict)

