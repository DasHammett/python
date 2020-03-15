import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv")
df.drop(columns = ["Province/State", "Lat", "Long", "3/14/20"], inplace = True)
df = pd.melt(df, "Country/Region")
df.index = df["variable"]
df.index.rename("Date", inplace = True)
df.drop(columns = "variable", inplace = True)
df.index = pd.to_datetime(df.index)

top9 = df.loc[df.index == df.index.max()].groupby("Country/Region").sum().nlargest(9, "value").index
df_top9 = df[df["Country/Region"].isin(top9)]
df_top9 = df_top9.groupby([df_top9.index, "Country/Region"]).sum().reset_index()

g = sns.FacetGrid(df_top9, col = "Country/Region", col_wrap=3, sharey=False)
g.map(plt.plot, "Date", "value")
g.set_xticklabels(rotation = 90)
plt.show()

df_top3 = df[df["Country/Region"].isin(["Spain","Italy","China"])]
df_top3 = df_top3.groupby([df_top3.index,"Country/Region"]).sum().reset_index()

sns.lineplot(data = df_top3,x = "Date", y = "value", hue = "Country/Region",style = "Country/Region",markers=["o","o","o"])
plt.xticks(rotation = 45)
plt.show()
