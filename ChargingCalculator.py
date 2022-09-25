class ChargingCalculator:

    import pprint
    import requests
    from dateutil import tz
    import datetime
    import json
    import pandas as pd
    # This is a sample Python script.

    # Press ⌃R to execute it or replace it with your code.
    # Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

    #Create a script that can gather irradiance data for the charging times 
        # and calculate ranges of minimum and maximum expected SOC increases during charging sessions. 
        # Output can be in the form of a bar graph. Stretch goal can be a Jupyter Notebook GUI that creates a JSON file of the parameters

        #use ghi value, convert different time from timezones to EST

        #after getting data from Solcast API through json file
        #we want the ghi value and time of day, make a list of dicts
        #ghi value every 30 min
        #change in ghi values in a list of dicts -> key is the time period end, value is change in ghi
        #Energy change(Watt hours) = change in irradiation(W/m^2) * array area(m^2) * solar system efficiency
        #*time period(hours)
        #for SR3, the array area was 4m^2

        #convert from UTC to CST

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
        pprint.pprint(apiCall)

        irradianceList = []
        timeList = []
        dataList = apiCall["forecasts"]
        #Gathering the irradiance from the JSON
        for ghi in dataList:
            irradianceList.append(ghi["ghi"])

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
        print(timeList)




    chargeSegment(33.786770, -84.406048, [])
    
