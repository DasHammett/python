"""
Python version: python3.7
"""
"""
Evolució del coronavirus basat en l'script en R d'Arnau Cangros.
Original en R disponible a: https://gitlab.com/acangros/coronavirus/-/blob/master/coronavirus.R
"""


import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import lock_datetime as dt
data = pd.read_json("https://pomber.github.io/covid19/timeseries.json")
formatter = mdates.DateFormatter("%d-%m")

appended_data = []
for col in data.columns:
    df = pd.json_normalize(data[col])
    df["Country"] = col
    appended_data.append(df)
df = pd.concat(appended_data)
df["date"] = pd.to_datetime(df["date"])


"""
Load US data
"""
urls = ["https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv",
        "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv", ]


def load_dataset(url):
    df = pd.read_csv(url)
    name = url.split(".")[-2].split("_")[-2]
    df = pd.concat([df.iloc[:, 6], df.iloc[:, 11:]], axis=1)
    df = df.groupby("Province_State").sum().reset_index()
    df = df.melt(id_vars="Province_State", var_name="date", value_name=name)
    df = df[df["date"] != "Population"]
    df["date"] = pd.to_datetime(df["date"])
    return df


us_confirmed = load_dataset(urls[0])
us_deaths = load_dataset(urls[1])

us_df = pd.merge(us_confirmed, us_deaths, on=["Province_State", "date"])
us_df.rename(columns={"Province_State": "Country"}, inplace=True)

df = pd.concat([df, us_df]).fillna(0)
df.drop_duplicates(inplace=True)
df = df[df["Country"] != "US"]

top9 = df[df["date"] == df["date"].max()].groupby(
    "Country")["confirmed"].sum().nlargest(9).index.to_list()
top9US = us_df[us_df["date"] == us_df["date"].max()].groupby(
    "Country")["confirmed"].sum().nlargest(9).index.to_list()


def covid_country(country, recovered=True, upper=100000, lower=50000):

    lastday = df["date"].max().strftime("%Y-%m-%d")

    def plotting(dataframe):
        increase = "+"+str(int(dataframe["confirmed"].diff().tail(1)))
        last = dataframe[dataframe["date"] ==
                         dataframe["date"].max()]["confirmed"].sum()
        deaths = int(dataframe["deaths"].tail(1))
        deathincrease = int(dataframe["deaths"].diff().tail(1))
        recovincrease = int(dataframe["recovered"].diff().tail(1))
        ax.plot(
            dataframe["date"],
            dataframe["confirmed"])
        # marker="o",
        # markerfacecolor="white",
        # markersize=4)
        ax.fill_between(
            dataframe["date"],
            0, dataframe["confirmed"],
            alpha=0.3)
        ax.bar(dataframe["date"], dataframe["deaths"]*-1, color="red")
        if recovered == True:
            recoverednum = int(dataframe["recovered"].tail(1))
            ax.bar(dataframe["date"], dataframe["recovered"], color="green")
            ax.annotate(
                f"Recov:{recoverednum} ({recovincrease})",
                xy=(0.05, 0.8),
                xycoords="axes fraction",
                fontsize=8,
                ha="left",
                va="bottom",
                color="green")
        ax.axhline(upper, color="red", ls=":", alpha=0.4)
        ax.axhline(lower, color="darkblue", ls=":", alpha=0.4)
        ax.annotate(
            f"Dead:{deaths} ({deathincrease})",
            xy=(0.05, 0.9),
            xycoords="axes fraction",
            fontsize=8,
            ha="left",
            va="bottom",
            color="red")
        ax.set_xticklabels(dataframe["date"], size=8, rotation=45, ha="right")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(7))
        ax.set_title(
            f"{country} - # infected: {last}\n ({increase} from previous day)",
            size=9)

    if isinstance(country, str):
        data = df[(df["Country"] == country) & (df["confirmed"] > 10)]
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
            data = df[(df["Country"] == country) & (df["confirmed"] > 10)]
            plotting(data)

        plt.tight_layout(w_pad=-3, h_pad=1)
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
    data["date"] = pd.to_datetime(data["date"], format="%Y/%m/%d")
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

"""
Spanish confirmed and deceased by gender and age group
"""

df = pd.read_csv(
    "https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/nacional_covid19_rango_edad.csv")
df.drop(index=df[df["rango_edad"] == "Total"].index, axis=1, inplace=True)
df = df[df["fecha"] == df["fecha"].max()]

fig, ax = plt.subplots()
rect1 = ax.barh(df.loc[df["sexo"] == "hombres", "rango_edad"],
                df.loc[df["sexo"] == "hombres", "casos_confirmados"],
                label="male", color="darkgrey", alpha=0.7, edgecolor="black")
rect2 = ax.barh(df.loc[df["sexo"] == "mujeres", "rango_edad"],
                df.loc[df["sexo"] == "mujeres", "casos_confirmados"] * -1,
                label="female", color="darkgrey", alpha=0.3, edgecolor="black")
rect3 = ax.barh(df.loc[df["sexo"] == "hombres", "rango_edad"],
                df.loc[df["sexo"] == "hombres", "fallecidos"],
                label="deceased", color="red", alpha=0.5, edgecolor="black")
rect4 = ax.barh(df.loc[df["sexo"] == "mujeres", "rango_edad"],
                df.loc[df["sexo"] == "mujeres", "fallecidos"] * -1,
                color="red", alpha=0.5, edgecolor="black")

def autolabel(rects, offset=(-15, 0)):
    for rect in rects:
        width = rect.get_width()
        ax.annotate("{}".format(abs(width)),
                    xy=(width, rect.get_y() + rect.get_height() / 2),
                    xytext=offset,
                    textcoords="offset points",
                    ha="center", va="center")

autolabel(rect1)
autolabel(rect2, offset=(15, 0))
ax.set_xticklabels([int(abs(x)) for x in ax.get_xticks()])
plt.legend()
plt.suptitle(
    "Spanish confirmed and deceased cases by age and gender\n (based on sample of confirmed cases)")
plt.show()

def rolling_14(countries):

    df_test = df[df["Country"].isin(countries)]
    df_test.sort_values(["Country", "date"], inplace=True)
    df_test["diff"] = df_test.groupby("Country")["confirmed"].diff()
    df_test["rolling14"] = df_test.groupby("Country")["diff"].apply(lambda x: x.rolling(14).mean())
    df_test = df_test.melt(id_vars=["Country", "date"])
    df_test = df_test[df_test["variable"].isin(["diff", "rolling14"])]
    df_test = df_test[df_test["date"] > "2020-02-20"]
    df_test = df_test.reset_index()
    df_test["cumsum"] = df_test[df_test["variable"] == "diff"].groupby("Country")["value"].cumsum()

    dfs = pd.read_html("https://en.wikipedia.org/wiki/National_responses_to_the_COVID-19_pandemic", header=1)
    df_lockdown = dfs[1].iloc[0:-1, 0:3]
    df_lockdown.loc[:, "Start date"] = pd.to_datetime(df_lockdown["Start date"].apply(lambda x: x.split("[")[0]))

    formatter = mdates.DateFormatter("%d-%m")

    max_value = int(df_test["value"].max())
    upper_bound = round(max_value/2, (len(str(max_value))-1) * -1)
    lower_bound = upper_bound/2

    fig, ax = plt.subplots(3, 3, sharex=True, sharey=False)
    for ax, country in zip(ax.flatten(), countries):
        data = df_test[df_test["Country"] == country]
        date = str(df_test["date"].max()).split()[0]
        max_confirmed = "{:,.0f}".format(int(data["cumsum"].max())).replace(",", ".")
        sns.lineplot(
            x="date",
            y="value",
            data=data[data["variable"] == "diff"],
            ax=ax,
            alpha=0.3,
            color="black",
            lw=0.5,
            label="daily"
        )
        sns.lineplot(
            x="date",
            y="value",
            data=data[data["variable"] == "rolling14"],
            ax=ax,
            label="rolling 14d"
        )
        ax.set_xticklabels(data.index, size=8, rotation=45, ha="right")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(7))
        ax.set_title(f"{country} - {max_confirmed} confirmed", size=10)
        ax.set_ylabel("")
        ax.set_xlabel("")
        ax.axhline(lower_bound, ls="-.", color="black", alpha=0.3, lw=0.5)
        ax.axhline(upper_bound, ls="-.", color="black", alpha=0.4, lw=0.5)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend_.remove()
        try:
            lockdown_date = df_lockdown.loc[(df_lockdown["Countries and territories"] == country) |
                                            (df_lockdown["Place"] == country),
                                            "Start date"].iloc[0]
        except IndexError:
            continue
        lockdown_date_14 = lockdown_date + dt.timedelta(days=14)
        for lock_date, text, color in zip([lockdown_date,lockdown_date_14],["lockdown","lockdown_14"],["red","green"]):
            ax.annotate(
                text,
                xy=(lock_date, (ax.get_ylim()[0] + ax.get_ylim()[1]) / 2),
                xytext=(-10, 0),
                textcoords="offset pixels",
                rotation=90,
                size=8,
                color=color,
                alpha=0.5,
                va="center")
            ax.axvline(lock_date, color = color, ls=":", lw=1, alpha = 0.7)
    plt.subplots_adjust(left=0.09, bottom=0.11, right=0.94, top=0.87, hspace=0.30, wspace=0.21)
    fig.legend(handles, labels, loc="upper left", frameon=True, ncol=2, bbox_to_anchor=( 0.01, 0.99))
    fig.suptitle(
        "Daily evolution of confirmed cases and 14 day rolling average\n for top 9 countries/regions by confirmed cases")
    fig.text(0.01, 0.01, f"Updated on {date}")
    plt.show()
