import urllib.request
import urllib.parse
import json
import pandas as pd
import datetime
import sys
import numpy as np

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
pd.set_option("display.max_columns", 500)
pd.set_option('display.expand_frame_repr', False)


class City():

    def __init__(self, city):
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
        "rain": " mm/h",
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
        "wind_deg": "º",
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
        "no2": "μg/m3",
        "o3": "μg/m3",
        "so2": "μg/m3",
        "nh3": "μg/m3",
        "pm2_5": "μg/m3",
        "pm10": "μg/m3",
        "air": ""
    }

    air_dict = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}

    df_poll_values = pd.DataFrame(
        {"type": ["no2", "pm10", "o3", "pm2_5", "so2"],
         "Good": [40, 20, 50, 10, 100],
         "Fair": [90, 40, 100, 20, 200],
         "Moderate": [120, 50, 130, 25, 350],
         "Poor": [230, 180, 240, 50, 500],
         "Very Poor": [340, 181, 380, 75, 750],
         "Extremely Poor": [341, 151, 381, 76, 752]
         },
        columns=["type", "Good", "Fair", "Moderate", "Poor", "Very Poor", "Extremely Poor"]
    )

    def __init__(self, city):
        City.__init__(self, city)
        API_WEATHER = "3"
        lat, lon = self.coordinates()
        url_and_param = "https://api.openweathermap.org/data/3.0/onecall?lat={}&lon={}&appid={}&units=metric&exlude=minutely,hourly".format(
            lat, lon, API_WEATHER)
        response = urllib.request.urlopen(url_and_param).read()
        response_dict = json.loads(response)
        url_and_param_pol = "http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={}&lon={}&appid={}".format(
            lat, lon, API_WEATHER)
        response_pol = urllib.request.urlopen(url_and_param_pol).read()
        response_dict_pol = json.loads(response_pol)
        self.__main_dict = response_dict["current"]
        self.__forecast_dict = response_dict["daily"]
        self.__pollution_dict = response_dict_pol["list"]

    def temp(self):
        temp = round(self.__main_dict["temp"], 1)
        real_temp = round(self.__main_dict["feels_like"], 1)
        return {"Temp": temp, "Feels like": real_temp}

    def weather(self):
        main_dict = self.__main_dict.copy()
        forecast_dict = self.__forecast_dict.copy()
        pollution_dict = self.__pollution_dict[0].copy()
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
                 "nh3",
                 "no",
                 "no2",
                 "o3",
                 "so2",
                 "pm2_5",
                 "pm10"]
        if "rain" not in main_dict.keys():
            main_dict["rainProb"] = round(forecast_dict[0]["pop"] * 100, 0)
            if "rain" in forecast_dict[0].keys():
                main_dict["rain"] = forecast_dict[0]["rain"]
            else:
                order.remove("rain")
        else:
            main_dict["rain"] = main_dict["rain"]["1h"]
            order.remove("rainProb")
        main_dict["wind_speed"] = round(main_dict["wind_speed"] * 3.6, 2)
        main_dict["visibility"] = round(main_dict["visibility"] / 1000, 2)
        main_dict["uvi"] = int(round(main_dict["uvi"], 0))
        main_dict["sunrise"] = datetime.datetime.fromtimestamp(main_dict["sunrise"]).strftime("%H:%M")
        main_dict["sunset"] = datetime.datetime.fromtimestamp(main_dict["sunset"]).strftime("%H:%M")
        main_dict.update(pollution_dict["components"])
        main_dict["air"] = self.air_dict[pollution_dict["main"]["aqi"]]

        for key in ["dt", "weather"]:
            main_dict.pop(key)
        main_dict = {key: main_dict[key] for key in order}
        super_dict = {k: str(main_dict[k]) + str(self.units_dict[k]) for k in main_dict}

        # Pollution
        df_poll = pd.json_normalize(pollution_dict).transpose()
        df_poll.reset_index(inplace=True)
        df_poll.columns = ["Type", "Value"]
        df_poll["Type"] = df_poll["Type"].str.split(".", expand=True)[1]
        df_poll_values = self.df_poll_values.melt(id_vars="type")
        df_poll_values["value"] = df_poll_values["value"].astype("int64")
        df_poll["Value"] = df_poll["Value"].astype("int64")

        df1 = pd.json_normalize(main_dict).transpose()
        units = pd.DataFrame.from_dict(self.units_dict, orient="index")
        df1 = df1.join(units, how="left", lsuffix="left", rsuffix="right")
        df1["merged"] = df1["0left"].astype("str") + df1["0right"].astype("str")
        df_pollution = pd.merge_asof(
            df_poll.sort_values(by="Value"),
            df_poll_values.sort_values(by="value"),
            left_by="Type",
            right_by="type",
            left_on="Value",
            right_on="value",
            direction="forward"
        )
        df1 = df1.reset_index()
        df1 = df1.merge(df_pollution[["variable", "Type"]], left_on="index", right_on="Type", how="left")
        df1["merged"] = df1["merged"] + [" ({})".format(str(x)) if pd.notna(x) else "" for x in df1["variable"]]
        df1.set_index(df1["index"], inplace=True)
        df1.index.names = [""]
        df1.index = [x.upper() if x in df_poll["Type"].unique() else x.capitalize() for x in df1.index]
        print(df1["merged"])

    def forecast(self):
        forecast_dict = self.__forecast_dict.copy()
        pollution_dict = self.__pollution_dict.copy()
        time = ["sunset", "sunrise", "moonrise", "moonset"]

        order = ["description",
                 "sunrise",
                 "sunset",
                 "moonrise",
                 "moonset",
                 "moon_phase",
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
                 "uvi",
                 "air",
                 "co",
                 "nh3",
                 "no",
                 "no2",
                 "o3",
                 "so2",
                 "pm2_5",
                 "pm10"]

        df_poll = pd.json_normalize(pollution_dict).set_index("dt")
        df_poll.index = pd.to_datetime(df_poll.index, unit="s")
        df_poll = round(df_poll.resample("D").mean(), 2)
        df_poll["main.aqi"] = df_poll["main.aqi"].apply(np.floor).map(self.air_dict)
        df_poll.columns = df_poll.columns.str.split(".").str[1]
        df_poll = df_poll.melt(ignore_index=False)
        self.df_poll_values = self.df_poll_values.melt(id_vars="type")
        self.df_poll_values["value"] = self.df_poll_values["value"].astype("float64")
        df_poll = df_poll.assign(New=pd.to_numeric(df_poll["value"], errors="coerce").fillna(0).round(4))
        df_poll["date"] = df_poll.index

        df_merged = pd.merge_asof(
            df_poll.sort_values(by="New"),
            self.df_poll_values[["value", "type", "variable"]].sort_values(by="value"),
            left_by="variable",
            right_by="type",
            left_on="New",
            right_on="value",
            direction="forward"
        ).set_index("date")
        df_merged["New"] = df_merged["New"].astype("str") + "μg/m3" + [" ({})".format(str(x)) if pd.notna(x) else "" for
                                                                       x in df_merged["variable_y"]]
        df_merged["New"] = [x if y == "aqi" else z for x, y, z in
                            zip(df_merged["value_x"], df_merged["variable_x"], df_merged["New"])]
        df_merged = df_merged.pivot(columns="variable_x", values="New")
        df_merged.index = df_merged.index.astype("str")

        time = ["sunset", "sunrise", "moonrise", "moonset"]
        for i, ele in enumerate(forecast_dict):
            forecast_dict[i].update(
                {k: str(datetime.date.fromtimestamp(v)) for (k, v) in forecast_dict[i].items() if "dt" in k})
            forecast_dict[i].update(
                {k: str(datetime.datetime.fromtimestamp(v).strftime("%H:%M")) for (k, v) in forecast_dict[i].items() if
                 any(x in k for x in time)})
            forecast_dict[i]["description"] = forecast_dict[i]["weather"][0]["description"]
            forecast_dict[i]["uvi"] = int(round(forecast_dict[i]["uvi"], 0))

        percent = ["moon_phase", "pop"]
        df = pd.json_normalize(forecast_dict).set_index("dt").melt(ignore_index=False).fillna(0)
        df.loc[df["variable"] == "moon_phase", "value"] = df.loc[df["variable"] == "moon_phase", "value"].apply(
            lambda x: x * 2 if x <= 0.5 else 2 - x * 2)
        df["value"] = df.apply(lambda x: int(round(x["value"] * 100, 0)) if x["variable"] in percent else x["value"],
                               axis=1)
        df.loc[df["variable"] == "pop", "variable"] = "rainProb"
        df["value"] = df["value"].astype("str") + df["variable"].map(self.units_dict)
        df = df.pivot(columns="variable", values="value")
        df_full_merge = pd.merge(df, df_merged, how="left", left_index=True, right_index=True).transpose()
        df_full_merge.columns = pd.to_datetime(df_full_merge.columns)
        df_full_merge.columns = [str(col).split()[0] + " (" + str(col.strftime("%a")) + ")" for col in
                                 df_full_merge.columns]
        df_full_merge.rename(index={"aqi": "air"}, inplace=True)
        df_full_merge = df_full_merge.reindex(order)
        df_full_merge.index = [x.upper() if x in df_poll["variable"].unique() else x.capitalize() for x in df_full_merge.index]
        print(df_full_merge)

if __name__ == '__main__':
    arg1 = "Barcelona"
    print("Getting weather for {}".format(City(arg1).location()))
    weather = Weather(arg1)
    print("Current weather")
    weather.weather()
    print("Forecaast")
    weather.forecast()
