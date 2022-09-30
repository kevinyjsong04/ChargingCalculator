import pprint
from pip._vendor import requests
from dateutil import tz
import datetime
import json
#import pandas as pd
# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

  #Create a script that can gather irradiance data for the charging times
    # and calculate ranges of minimum and maximum expected SOC increases during charging sessions.
    # Output can be in the form of a bar graph. Stretch goal can be a Jupyter Notebook GUI that creates a JSON file of the parameters

    #use ghi value, convert different time from timezones to EST

    #after getting data from Solcast API through json file
    #extract specifically the ghi values and put in a dict data structure
    #key is related to ghi, value is the value, also get times and convert
    #once all values are inside the dict, then use formula to calculate expected SOC increases

    #convert to SOC expected increased -> energy / (4.7 x 1000) x 100 to get percentage increase

    #have a UI that asks for time period and number of charging sessions --> 
    #give expected SOC percentage increases for each of the time periods

# This is our own class to add items to dictionary
class myDictionary(dict):
    
    def __init__(self):
        self = dict()

    def add(self, key, value):
        self[key] = value

def chargeSegment(latitude, longitude, date):
    soulcastAPI = "_3a3wT9RxwYesu6GW-ko4pmaAcxrqrW8"

    query = {
        "format":"json",
        "api_key":soulcastAPI,
        "Latitude":latitude,
        "Longitude":longitude,
        "hours":168
    }
    apiCall = requests.get("https://api.solcast.com.au/world_radiation/forecasts", params = query).json()
    #pprint.pprint(apiCall)

    irradianceList = []
    timeList = []
    dataList = apiCall["forecasts"]
    #Gathering the irradiance from the JSON
    for ghi in dataList:
        irradianceList.append(ghi["ghi"])

    # This adds
    for time in dataList:
        timing = time["period_end"]
        originalZone = tz.gettz("UTC") #Original timezone in UTC
        newTimeZone = tz.gettz("America/Chicago")
        timing = timing[:18:] + timing[-1] #
        utc = datetime.datetime.strptime(timing, "%Y-%m-%dT%H:%M:%SZ")
        utc.replace(tzinfo = originalZone)
        cst = utc.astimezone(newTimeZone)

        cst = str(cst)

        timeList.append(cst[:16]) #

    #print(irradianceList)
    #print(timeList)
    timeIrradianceDict = {"dateAndTime":timeList,
                          "irradiance":irradianceList}

    # As of right now, we are using SR3 values
    solarEfficiency = 0.80 # Value given from Bailey for SR3
    arrayArea = 4; # in m^2 for SR3
    time = 0.5

    #Makes the list of energy values in Wh
    energyList = []
    for i in range(0, len(irradianceList)):
        energy = irradianceList[i] * arrayArea * solarEfficiency * time
        energyList.append(energy)

    # Makes a list of energy percentage values
    energyPercentage = []
    for i in range(0, len(energyList)):
        energyPercent = float((energyList[i] / 4700.00) * 100)
        formattedPercentage = "{:.3f}".format(energyPercent) #formatting to 3 decimal places
        energyPercentage.append(formattedPercentage)
    
    #Put these values in a dictionary
    timeEnergyPair = myDictionary()
    for i in range(0, len(timeList)):
        timeEnergyPair.add(timeList[i], irradianceList[i])

    pprint.pprint(timeEnergyPair)
    #return timeEnergyPair


chargeSegment(38.927142183, -95.676805255, [])

'''
def generateGraphData(segments, start, end, energyData):
    
    # loop through each segment
    
'''




#testLatitude = 38.927142183
#testLongitude = -95.676805255
# Asking for latitude and longitude

#latitude = float(input("Enter latitude of location: "))
#longitude = float(input("Enter longitude of location: "))
#numOfSegments = input(int("Enter the number of segments of charge"))
#segmentArray = []
#for i in range(0, numOfSegments):
#    segmentArray.append(i + 1)
#startTime = []
#endTime = []
#for i in range(0, numOfSegments):
#    startTime[i] = input("Enter start time -> format example: xxxx-xx-xx xx:xx or 2022-09-29 08:00:")
#    endTime[i] = input("Enter end time -> format example: xxxx-xx-xx xx:xx or 2022-09-29 08:30:")


#generateGraphData(numOfSegments, startTime, endTime, energyPercentDict)
