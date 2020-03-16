"""
Python version: python3.7
"""
"""
Evolució del coronavirus basat en l'script en R d'Arnau Cangros.
Original en R disponible a: https://gitlab.com/acangros/coronavirus/-/blob/master/coronavirus.R
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter

formatter = DateFormatter("%Y-%m-%d")

df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv")
df.drop(columns = ["Province/State", "Lat", "Long"], inplace = True)
df.dropna(axis = 1, how = "all",inplace = True)
df = pd.melt(df, "Country/Region")
df.index = df["variable"]
df.index.rename("Date", inplace = True)
df.drop(columns = "variable", inplace = True)
df.index = pd.to_datetime(df.index)

top9 = df.loc[df.index == df.index.max()].groupby("Country/Region").sum().nlargest(9, "value").index
df_top9 = df[df["Country/Region"].isin(top9)]
df_top9 = df_top9.groupby([df_top9.index, "Country/Region"]).sum().reset_index()

fig, axes = plt.subplots(3,3, sharex = True)
for ax, country in zip(axes.flatten(), top9):
    df0 = df_top9[df_top9["Country/Region"] == country]
    increase = "+"+str(int((df0["value"] - df0.shift(1)["value"]).tail(1)))
    last = df0.loc[df0.index == df0.index.max(),"value"].sum()
    ax.plot(df0["Date"], df0["value"], color="#6C6262",marker="o", markersize=3, linewidth=1, mfc = "#B4F38E")
    ax.axhline(10000, color = "red")
    ax.axhline(5000, color = "#E1A994")
#    ax.tick_params(axis="x",labelrotation=90)
    ax.set_xticklabels(df0["Date"], rotation = 45, ha = "right")
    ax.xaxis.set_major_formatter(formatter)
    ax.set_title(f"{country} - # infected: {last}\n ({increase} from prev day)",size=9)
plt.tight_layout(w_pad = -0.1, h_pad = 1.1)
fig.suptitle("COVID-19 infected population by Country. Top 9 by volume", ha = "center")
plt.subplots_adjust(left=0.11,bottom=0.22, right= 0.94, top = 0.87, wspace = 0.38, hspace = 0.45)
plt.show()

u = df_top9["Country/Region"].unique()
fig, axes = plt.subplots(ncols = 3,nrows=3, figsize = (10,3))
for country, ax in zip(u, axes):
    df_top9[df_top9["Country/Region"] == country].plot(title = country, ax = ax, y="value", x = "Date")
plt.tight_layout()
plt.show()

