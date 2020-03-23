"""
Python version: python3.7
"""
"""
Evolució del coronavirus basat en l'script en R d'Arnau Cangros.
Original en R disponible a: https://gitlab.com/acangros/coronavirus/-/blob/master/coronavirus.R
"""


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
data = pd.read_json("https://pomber.github.io/covid19/timeseries.json")
formatter = mdates.DateFormatter("%d-%m")

appended_data = []
for col in data.columns:
    df = pd.json_normalize(data[col])
    df["Country"] = col
    appended_data.append(df)
df = pd.concat(appended_data)
df = df.reset_index()
df["date"] = pd.to_datetime(df["date"])

top9 = df[df["date"] == df["date"].max()].groupby(
    "Country")["confirmed"].sum().nlargest(9).index
df_top9 = df[df["Country"].isin(top9)]


def covid_country(country):

    lastday = df["date"].max().strftime("%Y-%m-%d")

    def plotting(dataframe):
        increase = "+"+str(
            int((dataframe["confirmed"] - dataframe.shift(1)["confirmed"]).tail(1)))
        last = dataframe[dataframe["date"] ==
                         dataframe["date"].max()]["confirmed"].sum()
        deaths = int(dataframe["deaths"].tail(1))
        recovered = int(dataframe["recovered"].tail(1))
        ax.plot(
            dataframe["date"],
            dataframe["confirmed"],
            marker="o",
            markerfacecolor="white",
            markersize=4)
        ax.fill_between(
            dataframe["date"],
            0, dataframe["confirmed"],
            alpha=0.3)
        ax.bar(dataframe["date"], dataframe["deaths"]*-1, color="red")
        ax.bar(dataframe["date"], dataframe["recovered"], color="green")
        ax.axhline(10000, color="red", ls=":", alpha=0.4)
        ax.axhline(5000, color="darkblue", ls=":", alpha=0.4)
        ax.text(
            0.01,
            0.9,
            f"Dead:{deaths}",
            transform=ax.transAxes,
            size=8,
            color="red")
        ax.text(
            0.01,
            0.78,
            f"Recov:{recovered}",
            transform=ax.transAxes,
            size=8,
            color="green")
        ax.set_xticklabels(dataframe["date"], rotation=45, ha="right", size=8)
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.set_title(
            f"{country} - # infected: {last}\n ({increase} from previous day)",
            size=9)

    if isinstance(country, str):
        data = df[df["Country"] == country]
        fig, ax = plt.subplots()
        plotting(data)
        fig.suptitle(
            f"COVID-19 infected population for {country}\n Last update: {lastday}")
        plt.subplots_adjust(left=0.09, bottom=0.16, right=0.94, top=0.87)
        plt.show()

    else:
        countries = list(country)
        list_length = len(countries)
        if list_length < 3:
            m = 2
            n = 1
        elif list_length == 4:
            m = 2
            n = 2
        else:
            m = 3
            if list_length % 3 == 0:
                n = int(list_length / 3)
            else:
                n = int(list_length // 3 + 1)
        over_plots = int(m*n - list_length)
        if m * n == list_length:
            fig, axes = plt.subplots(n, m, sharex=True)
        else:
            fig, axes = plt.subplots(n, m)
        for ax, country in zip(axes.flatten(), countries):
            data = df[df["Country"] == country]
            plotting(data)

        plt.tight_layout(w_pad=-2, h_pad=1)
        fig.suptitle(
            f"COVID-19 infected population by Country/Region. Top 9 by volume\n Last update: {lastday}")
        plt.subplots_adjust(left=0.09, bottom=0.16, right=0.94, top=0.87)
        for i in range(1, over_plots+1):
            axes.flat[-i].set_visible(False)
        plt.show()


"""
COVID-19 for Spain, by region
"""


def carga_datos(url):
    data = pd.read_csv(url)
    data.drop(columns="cod_ine", inplace=True)
    data.drop(index=data[data["CCAA"] == "Total"].index, inplace=True)
    data = pd.melt(data, "CCAA")
    data.rename(columns={"variable": "date"}, inplace=True)
    data["date"] = pd.to_datetime(data["date"], format="%d/%m/%Y")
    return data


urls = ["https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_casos.csv",
        "https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_altas.csv",
        "https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_fallecidos.csv"]

appended_df = []
for url in urls:
    df = carga_datos(url)
    name = url.split(".")[-2].split("_")[-1]  # get word before extension
    df.rename(columns={"value": name}, inplace=True)
    appended_df.append(df)

df = pd.concat([df.set_index(["date", "CCAA"])
                for df in appended_df], axis=1).reset_index()
df.rename(
    columns={
        "casos": "confirmed",
        "altas": "recovered",
        "fallecidos": "deaths",
        "CCAA": "Country"},
    inplace=True)
df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y")

top9CCAA = df[df["date"] == df["date"].max()].groupby(
    "Country").sum().nlargest(9, "confirmed").index
df_top9 = df[df["Country"].isin(top9CCAA)]
