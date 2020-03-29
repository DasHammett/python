#!/usr/bin/python3

import urllib.request
import urllib.parse
import json
import pandas as pd
import datetime
import sys

pd.set_option("display.max_columns", 500)
pd.set_option('display.expand_frame_repr', False)

arg1 = sys.argv[1]

class City():

    def __init__(self,city):
        self.city = city
        API_GEO = "pk.eyJ1IjoiaGFtbWV0dCIsImEiOiJjanBzdmhoNmMxMXdjNDZteDNmZ3A3ZzdpIn0.N0bVWWOEet21WUumGxW9oA"
        url_and_params = "https://api.mapbox.com/geocoding/v5/mapbox.places/" + urllib.parse.quote(city) + \
        ".json?types=place&autocomplete=false&access_token=" + API_GEO
        response = urllib.request.urlopen(url_and_params).read()
        response_dict = json.loads(response)
        self.__main_dict = response_dict["features"][0]

    def coordinates(self):
        coordinates = self.__main_dict["geometry"]["coordinates"][::-1]
        return coordinates

    def location(self):
        location = self.__main_dict["place_name"]
        return location

    def __str__(self):
        return f"{self.location()} is at coordinates {self.coordinates()}"


class Weather(City):

    units_dict = {
        'summary': "",
        "moonPhase": "%",
        "precipIntensityMax":" mm/h",
        'nearestStormDistance': " Km",
        'nearestStormBearing': "º",
        'precipIntensity': " mm/h",
        'precipAccumulation': " mm/h",
        'precipProbability': "%",
        'precipType': "",
        'temperature': "ºC",
        'apparentTemperature': "ºC",
        'dewPoint': "ºC",
        'humidity': "%",
        'pressure': " hPa",
        'windSpeed': " Km/h",
        'windGust': " Km/h",
        'windBearing':"º",
        'cloudCover': "%",
        'uvIndex': "",
        'visibility': " Km",
        'ozone': " DU",
        "temperatureMin": "ºC",
        "temperatureMax": "ºC",
        "apparentTemperatureMin": "ºC",
        "apparentTemperatureMax": "ºC"
        }

    def __init__(self,city):
        City.__init__(self,city)
        API_WEATHER = "21d25c5471d4dc5962ada39bbbc3208a"
        latlong = ",".join(str(x) for x in self.coordinates())
        url_and_param = "https://api.darksky.net/forecast/" + API_WEATHER + "/" + latlong + "?units=si"
        response = urllib.request.urlopen(url_and_param).read()
        response_dict = json.loads(response)
        self.__main_dict = response_dict["currently"]
        self.__forecast_dict = response_dict["daily"]["data"]

    def temp(self):
        temp = round(self.__main_dict["temperature"],1)
        real_temp = round(self.__main_dict["apparentTemperature"], 1)
        return {"Temp": temp,"Feels like": real_temp}

    def weather(self):
        main_dict = self.__main_dict.copy()
        main_dict["cloudCover"] = round(main_dict["cloudCover"] * 100, 2)
        main_dict["humidity"] = round(main_dict["humidity"] * 100, 2)
        main_dict["precipProbability"] = round(main_dict["precipProbability"] * 100, 0)
        main_dict["windSpeed"] = round(main_dict["windSpeed"] * 3.6, 2)
        main_dict["windGust"] = round(main_dict["windGust"] * 3.6, 2)
        for key in ["time","icon"]:
             main_dict.pop(key)
        length = []
        for value in main_dict.values():
            length.append(len(str(value)))
        length = max(length) + 5
        super_dict = {k: str(main_dict[k]) + str(self.units_dict[k]) for k in main_dict}
        for key,value in super_dict.items():
            print("{:<20} --> {:>{x}}".format(key[0].upper() + key[1:] ,value,x=length))

    def forecast(self):
        forecast_dict = self.__forecast_dict.copy()
        for i, ele in enumerate(forecast_dict):
            forecast_dict[i] = {k:v for (k,v) in forecast_dict[i].items() if not any(x in k for x in ["Time","High","Low"])}
            forecast_dict[i].update({k:str(datetime.date.fromtimestamp(v)) for (k,v) in forecast_dict[i].items() if "time" in k})

        df = pd.DataFrame.from_dict(forecast_dict).transpose()
        df.columns = df.loc["time"]
        df = df.drop(labels = ["time","icon"], axis = 0)
        percent = ["moonPhase", "precipProbability",  "humidity", "cloudCover"]
        df.loc[percent] *= 100
        df.loc[percent] = df.loc[percent].astype(int)

        for i in df.index:
            df.loc[i] = df.loc[i].astype(str) + self.units_dict[i]

        df = df.reindex(self.units_dict)
        df.dropna(inplace = True)
        print(df)

if arg1 == "weather":
    Weather("Barcelona").weather()
else:
    Weather("Barcelona").forecast()
