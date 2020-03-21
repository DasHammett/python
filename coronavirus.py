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
        if m == n:
            fig, axes = plt.subplots(n, m, sharex=True)
        else:
            fig, axes = plt.subplots(n, m)
        for ax, country in zip(axes.flatten(), countries):
            data = df[df["Country"] == country]
            plotting(data)

        plt.tight_layout(w_pad=-2, h_pad=1)
        fig.suptitle(
            f"COVID-19 infected population by Country. Top 9 by volume\n Last update: {lastday}")
        plt.subplots_adjust(left=0.09, bottom=0.16, right=0.94, top=0.87)
        for i in range(1, over_plots+1):
            axes.flat[-i].set_visible(False)
        plt.show()


"""
COVID-19 for Spain, by region
"""
df = pd.read_csv(
    "https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_casos.csv")
df.drop(columns="cod_ine", inplace=True)
df.drop(index=df[df["CCAA"] == "Total"].index, inplace=True)
df = pd.melt(df, "CCAA")
df.rename(columns={"variable": "Date"}, inplace=True)
df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")

top9CCAA = df[df["Date"] == df["Date"].max()].groupby(
    "CCAA").sum().nlargest(9, "value").index
df_top9CCAA = df[df["CCAA"].isin(top9CCAA)]

fig, axes = plt.subplots(3, 3, sharex=True)
for ax, ccaa in zip(axes.flatten(), top9CCAA):
    #locator = mdates.AutoDateLocator(minticks = 3, maxticks = 10)
    df0 = df_top9CCAA[df_top9CCAA["CCAA"] == ccaa]
    lastday = df_top9CCAA["Date"].max().strftime("%Y-%m-%d")
    increase = "+"+str(int((df0["value"] - df0.shift(1)["value"]).tail(1)))
    last = df0[df0["Date"] == df0["Date"].max()]["value"].sum()
    ax.plot(df0["Date"], df0["value"])
    ax.fill_between(df0["Date"], 0, df0["value"], alpha=0.3)
    ax.axhline(1000, color="red", ls=":", alpha=0.4)
    ax.axhline(500, color="darkblue", ls=":", alpha=0.4)
    ax.set_xticklabels(df0["Date"], rotation=45, ha="right")
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.set_title(
        f"{ccaa} - # infected: {last}\n ({increase} from previous day)",
        size=9)
plt.tight_layout(w_pad=-4, h_pad=1)
fig.suptitle(
    f"COVID-19 infected population by region in Spain. Top 9 by volume\n Last update: {lastday}")
plt.subplots_adjust(left=0.09, bottom=0.16, right=0.94, top=0.87)
plt.show()
