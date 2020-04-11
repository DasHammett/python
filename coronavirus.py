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
    "Country")["confirmed"].sum().nlargest(9).index


def covid_country(country, recovered=True):

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
            ax.text(
                0.01,
                0.78,
                f"Recov:{recoverednum} ({recovincrease})",
                transform=ax.transAxes,
                size=8,
                color="green")
        ax.axhline(100000, color="red", ls=":", alpha=0.4)
        ax.axhline(50000, color="darkblue", ls=":", alpha=0.4)
        ax.text(
            0.01,
            0.9,
            f"Dead:{deaths} ({deathincrease})",
            transform=ax.transAxes,
            size=8,
            color="red")
        ax.set_xticklabels(dataframe["date"], size=8, rotation=45, ha="right")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(7))
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


"""
Death daily evolution
"""

df_test = pd.crosstab(
    df_top9.date,
    df_top9.Country,
    values=df_top9.deaths,
    aggfunc="sum").diff().dropna()

text = pd.DataFrame(df_test[-1:].T).unstack().sort_values()
text = text.to_frame(name="value")
text["Diff"] = text.diff().fillna(0)
text.reset_index(inplace=True)

text["test"] = np.where(
    (text["Diff"].diff().fillna(0) > 0) & (
        text["Diff"] < 10), 5, np.where(
            (text["Diff"].diff().fillna(0) < 0) & (
                text["Diff"] < 10), -10, 0))
text["test"] = np.where((text["Diff"] == 0) & (
    text["test"].shift(-1) < 0), -10, text["test"])

locator = mdates.AutoDateLocator()
formatter = mdates.ConciseDateFormatter(locator)
fig, ax = plt.subplots()
for col in df_test.columns:
    ax.plot(
        df_test.index,
        df_test[col],
        marker="o",
        markersize=4,
        markerfacecolor="white",
        markeredgecolor=None)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    #ax.annotate("{}".format(col),xy=(plt.xticks()[0][-1], df_test[col].iloc[-1]),xytext=(5,0), textcoords="offset pixels")
    ax.annotate("{}".format(col),
                xy=(df_test.index.max(), df_test[col].iloc[-1]),
                xytext=(25, text.loc[text["Country"] == col]["test"]-2),
                # xytext=(20,0),
                textcoords="offset pixels",
                arrowprops=dict(
                    color=ax.get_lines()[-1].get_c(),
                    arrowstyle="-|>", linewidth=0.5)
                )
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_minor_locator(mdates.DayLocator())
plt.xlim([df_test.index.min(), df_test.index.max()+datetime.timedelta(days=1)])
plt.title("# COVID-19 deaths evolution\nTop9 infected Countries")
plt.tight_layout()
plt.subplots_adjust(
    left=0.09,
    bottom=0.12,
    right=0.88,
    top=0.89,
    hspace=0.2,
    wspace=0.2)
plt.show()


fig, ax = plt.subplots()
sns.heatmap(data=df_test[-20:].T,
            square=True,  # make cells square
            cbar_kws={'fraction': 0.01},  # shrink colour bar
            cmap='OrRd',  # use orange/red colour map
            linewidth=1,
            annot=True,
            fmt=".0f",
            annot_kws={"size": 8}
            )
ax.set_xticklabels(df_test[-20:].T.columns.strftime('%d-%m'))
ax.set_xlabel("")
ax.set_ylabel("")
plt.title(
    "Number of COVID-19 deceased for the last 20 days.\n Top countries by infection")
plt.xlabel()
plt.ylabel()
plt.show()


distancia = pd.DataFrame(text[["Country", "value"]].copy())
distancia["Diff"] = distancia["value"].diff().fillna(0)
distancia["test"] = distancia["value"].diff().sub(
    distancia["value"].diff(-1)).fillna(0) / 2

distancia["test2"] = pd.Series(np.where((distancia["Diff"] < 10) & (distancia["Diff"].shift(-1) > distancia["Diff"].shift()), distancia["test"],
                                        np.where((distancia["Diff"] < 10) & (distancia["Diff"].shift(-1) < distancia["Diff"].shift()), -distancia["test"],
                                                 np.where((distancia["Diff"] == 0) & (distancia["Diff"].shift(-1) < distancia["Diff"].shift(-2)), distancia["value"]/2,
                                                          np.where((distancia["Diff"] == 0) & (distancia["Diff"].shift(-1) > distancia["Diff"].shift(-2)), -distancia["value"]/2,
                                                                   0)))))


def spacing(data):
    df = pd.DataFrame(data[["Country", "value"]].copy())
    original_value = df[["value"]]
    round = 0
    while round < 6:
        if round > 0:
            df["value"] = df["value2"]
        df["Diff"] = df["value"].diff().fillna(0)
        df["test"] = df["value"].diff().sub(df["value"].diff(-1)).fillna(0)/2
        df["test2"] = pd.Series(np.where((df["Diff"] < 10) & (df["Diff"].shift(-1) > df["Diff"].shift()), df["test"],
                                         np.where((df["Diff"] < 10) & (df["Diff"].shift(-1) < df["Diff"].shift()), -df["test"],
                                                  np.where((df["Diff"] == 0) & (df["Diff"].shift(-1) < df["Diff"].shift(-2)), df["value"]/2,
                                                           np.where((df["Diff"] == 0) & (df["Diff"].shift(-1) > df["Diff"].shift(-2)), -df["value"]/2,
                                                                    0)))))
        df["value2"] = df["value"] + df["test2"]
        round += 1
        df["final"] = df["value2"].sub(original_value["value"])
    return df
