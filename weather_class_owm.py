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
arg2 = sys.argv[2]

class City():

    def __init__(self,city):
        self.city = city
        API_GEO = ""
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
        "description": "",
        "sunrise": "",
        "sunset": "",
        "moon_phase": "%",
        "moonrise": "",
        "moonset": "",
        "rain":" mm/h",
        "rainProb": "%",
        "temp.day": "ºC",
        "temp": "ºC",
        "temp.morn": "ºC",
        "temp.eve": "ºC",
        "temp.night": "ºC",
        "temp.min": "ºC",
        "temp.max": "ºC",
        "feels_like": "ºC",
        "feels_like.day": "ºC",
        "feels_like.morn": "ºC",
        "feels_like.eve": "ºC",
        "feels_like.night": "ºC",
        "feels_like.min": "ºC",
        "feels_likes.max": "ºC",
        "dew_point": "ºC",
        "humidity": "%",
        "pressure": " hPa",
        "wind_speed": " Km/h",
        "wind_gust": " Km/h",
        "wind_deg":"º",
        "clouds": "%",
        "uvi": "",
        "visibility": " Km",
        "ozone": " DU",
        "temperatureMin": "ºC",
        "temperatureMax": "ºC",
        "apparentTemperatureMin": "ºC",
        "apparentTemperatureMax": "ºC",
        "co": "μg/m3",
        "no": "μg/m3",
        "no2":"μg/m3",
        "o3": "μg/m3",
        "so2": "μg/m3",
        "nh3": "μg/m3",
        "pm2_5": "μg/m3",
        "pm10": "μg/m3",
        "air":""
        }

    air_dict = {1: "Good", 2:"Fair", 3:"Moderate", 4:"Poor", 5:"Very Poor"}

    def __init__(self,city):
        City.__init__(self,city)
        API_WEATHER = ""
        lat,lon = self.coordinates()
        url_and_param = "https://api.openweathermap.org/data/3.0/onecall?lat={}&lon={}&appid={}&units=metric&exlude=minutely,hourly".format(lat,lon,API_WEATHER)
        response = urllib.request.urlopen(url_and_param).read()
        response_dict = json.loads(response)
        url_and_param_pol = "http://api.openweathermap.org/data/2.5/air_pollution?lat={}&lon={}&appid={}".format(lat,lon,API_WEATHER)
        response_pol = urllib.request.urlopen(url_and_param_pol).read()
        response_dict_pol = json.loads(response_pol)
        self.__main_dict = response_dict["current"]
        self.__forecast_dict = response_dict["daily"]
        self.__pollution_dict = response_dict_pol["list"]


    def temp(self):
        temp = round(self.__main_dict["temp"],1)
        real_temp = round(self.__main_dict["feels_like"], 1)
        return {"Temp": temp,"Feels like": real_temp}

    def weather(self):
        main_dict = self.__main_dict.copy()
        forecast_dict = self.__forecast_dict.copy()
        pollution_dict = self.__pollution_dict.copy()
        main_dict["description"] = main_dict["weather"][0]["description"]
        order = ["description",
                 "sunrise",
                 "sunset",
                 "temp",
                 "feels_like",
                 "humidity",
                 "rainProb",
                 "rain",
                 "pressure",
                 "dew_point",
                 "uvi",
                 "clouds",
                 "visibility",
                 "wind_speed",
                 "wind_deg",
                 "air",
                 "co",
                 "no",
                 "no2",
                 "o3",
                 "so2",
                 "nh3",
                 "pm2_5",
                 "pm10"]
        if "rain" not in main_dict.keys():
            main_dict["rainProb"] = round(forecast_dict[0]["pop"] * 100, 0)
            order.remove("rain")
        else:
            main_dict["rain"] = main_dict["rain"]["1h"]
            order.remove("rainProb")
        main_dict["wind_speed"] = round(main_dict["wind_speed"] * 3.6, 2)
        main_dict["visibility"] = round(main_dict["visibility"]/1000,2)
        main_dict["uvi"] = int(round(main_dict["uvi"],0))
        main_dict["sunrise"] = datetime.datetime.fromtimestamp(main_dict["sunrise"]).strftime("%H:%M")
        main_dict["sunset"] = datetime.datetime.fromtimestamp(main_dict["sunset"]).strftime("%H:%M")
        main_dict.update(pollution_dict[0]["components"])
        main_dict["air"] = self.air_dict[pollution_dict[0]["main"]["aqi"]]

        for key in ["dt","weather"]:
             main_dict.pop(key)
        length = []
        for value in main_dict.values():
            length.append(len(str(value)))
        length = max(length) + 5
        main_dict = {key:main_dict[key] for key in order}
        super_dict = {k: str(main_dict[k]) + str(self.units_dict[k]) for k in main_dict}
        for key,value in super_dict.items():
            print("{:<20} --> {:>{x}}".format(key[0].upper() + key[1:] ,value,x=length))

    def test(self):
        print(self.__forecast_dict)

    def forecast(self):
        forecast_dict = self.__forecast_dict.copy()
        time = ["sunset","sunrise","moonrise","moonset"]
        for i, ele in enumerate(forecast_dict):
            #forecast_dict[i] = {k:v for (k,v) in forecast_dict[i].items() if not any(x in k for x in ["Time","High","Low"])}
            forecast_dict[i].update({k:str(datetime.date.fromtimestamp(v)) for (k,v) in forecast_dict[i].items() if "dt" in k})
            forecast_dict[i].update({k:str(datetime.datetime.fromtimestamp(v).strftime("%H:%M")) for (k,v) in forecast_dict[i].items() if any(x in k for x in time)})
            forecast_dict[i]["description"] = forecast_dict[i]["weather"][0]["description"]
            forecast_dict[i]["uvi"] = int(round(forecast_dict[i]["uvi"],0))
        #    forecast_dict[i].pop("weather")
        order = ["description",
                 "sunrise",
                 "sunset",
                 "moonrise",
                 "moonset",
                 "temp.day",
                 "temp.morn",
                 "temp.eve",
                 "temp.night",
                 "temp.min",
                 "temp.max",
                 "feels_like.day",
                 "feels_like.morn",
                 "feels_like.eve",
                 "feels_like.night",
                 "clouds",
                 "rainProb",
                 "rain",
                 "pressure",
                 "humidity",
                 "dew_point",
                 "wind_speed",
                 "wind_gust",
                 "wind_deg",
                 "uvi"]
        #df = pd.DataFrame.from_dict(forecast_dict).transpose()
        df = pd.json_normalize(forecast_dict).transpose()
        df.columns = df.loc["dt"]
        df = df.drop(labels = ["dt"], axis = 0)
        df.columns = pd.to_datetime(df.columns)
        df.columns = [str(col).split()[0] + " ("+str(col.strftime("%a"))+")" for col in df.columns]
        percent = ["moon_phase","pop"]
        df.loc[percent] *= 100
        df.loc[percent] = df.loc[percent].astype(int)
        df.rename(index={"pop":"rainProb"},inplace = True)
        df = df.reindex(order)

        for i in df.index:
            df.loc[i] = df.loc[i].astype(str) + self.units_dict[i]

        df.dropna(inplace = True)
        print(df)

    def dwm(self):
        main_dict = self.__main_dict.copy()
        forecast_dict = self.__forecast_dict.copy()
        weather_icon = main_dict["weather"][0]["icon"]


if arg1 == "weather":
    Weather(arg2).weather()
else:
    Weather(arg2).forecast()
