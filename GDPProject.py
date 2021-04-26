import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
# import seaborn as sns

gdp_data = pd.read_csv("GDP Hist.csv")
print(gdp_data.head())
print(gdp_data.info())

# data has 2 entries per year for: total in millions & GDP per person
# removing duplicates based on years to leave only total in millions
gdp_data.drop_duplicates(subset=["LOCATION", "TIME"], inplace=True)

print(gdp_data["MEASURE"].unique())  # Check only millions in USD remains

# Create list of unneeded columns & remove
unneeded_cols = ["INDICATOR", "SUBJECT", "MEASURE", "FREQUENCY", "Flag Codes"]
gdp_data.drop(columns=unneeded_cols, axis=1, inplace=True)
print(gdp_data.info())


# Don't have full information for every year - so check how many entries
pd.set_option("display.max_rows", None)     # So can see full set of counts per year
list_years = gdp_data["TIME"].value_counts()
list_years.sort_index(axis=0, ascending=False, inplace=True)
print(list_years)

######### 2019 TOTALS #########

# Lacking info for 2020 so looking at 2019 figures
gdp2019 = gdp_data[gdp_data["TIME"] == 2019].copy()
print(gdp2019)

# Dropping OECD, OECDE, EU28, EU27_2020, EA19 so that we only have individual countries
gdp2019 = gdp2019.drop(index=[3798, 3874, 3723, 4810, 4173])
pd.options.display.float_format = '{:,.2f}'.format
gdp2019.sort_values('Value', inplace=True)
gdp2019['rank'] = gdp2019['Value'].rank(ascending=0)
print(gdp2019)

ax = gdp2019.plot(x='LOCATION', y='Value', rot=60, kind='bar', title='GDP per country 2019, in millions USD')
ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
ax.annotate("IRL - 29th largest GDP", xy=[21, 450000], xytext=(12, 3500000), arrowprops={'arrowstyle': '->', 'color': 'grey'})
plt.show()


######### All countries growth 1970 - 2019 #########

# Prior to 1970 don't have much information
# Therefore subset for 1970 & 2019 figures
gdp1970 = gdp_data[gdp_data["TIME"] == 1970].copy()
gdp2019 = gdp_data[gdp_data["TIME"] == 2019].copy()
gdp_growth = gdp1970.merge(gdp2019, on="LOCATION", suffixes=['_1970', '_2019'])

# Create function to calc average returns
def avgrowth(row):
    return((row["Value_2019"]-row["Value_1970"])/row["Value_1970"])*100


gdp_growth["%Growth"] = gdp_growth.apply(avgrowth, axis=1)
gdp_growth.sort_values("%Growth", inplace=True)
print(gdp_growth)

gdp_growth.plot(x="LOCATION", y="%Growth", kind='bar', rot=45, title='GDP Growth 1970-2019')
plt.xlabel("Country")
plt.ylabel("% Growth")
plt.tight_layout()
plt.show()


######### Ireland Annual Growth % #########

gdp_ire = gdp_data[gdp_data['LOCATION'] == "IRL"].copy()
gdp_ire.set_index('TIME', inplace=True)
gdp_ire['Annual%'] = np.nan       # insert blank column

# loop through dataframe & calc annual % growth
for i in gdp_ire.index:
    if i == 1970:
        gdp_ire.loc[i, 'Annual%'] = 0
    else:
        gdp_ire.loc[i, 'Annual%'] = (gdp_ire.loc[i, 'Value']-gdp_ire.loc[i-1, 'Value'])/gdp_ire.loc[i-1, 'Value']*100

print(gdp_ire)


def quickplot(axes, x, y, color, title, xlabel, ylabel, label):
    axes.plot(x, y, color=color, label=label)
    axes.set(title=title, xlabel=xlabel)
    axes.set_ylabel(ylabel, color=color)


fig, ax = plt.subplots()
quickplot(ax, gdp_ire.index, gdp_ire['Value'], 'red', 'Ireland GDP Growth', 'Year', 'GDP in millions USD', '')
ax2 = ax.twinx()
quickplot(ax2, gdp_ire.index, gdp_ire["Annual%"], 'blue', 'Ireland GDP Growth', 'Year', 'Annual % Growth', '')
ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
plt.axhline(y=0, color='grey', linestyle='--', alpha=0.3)
plt.show()


######### Ireland vs Tax Data #########

# Subset for Ireland GDP
gdp_ire = gdp_data[gdp_data['LOCATION'] == "IRL"].copy()
print(gdp_ire.info())

# Create dict of years & tax rates & combine with Ireland DF
taxrate_dict = {'TIME': [1970, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003],
                'TaxRate': [40, 38, 36, 32, 28, 24, 20, 16, 12.5]}

taxrate_df = pd.DataFrame(taxrate_dict)
gdp_ire = gdp_ire.merge(taxrate_df, on='TIME', how='left')

# Forward filling in for the tax years missing info
gdp_ire = gdp_ire.fillna(method='ffill', axis=0)
print(gdp_ire)

fig, ax = plt.subplots()
quickplot(ax, gdp_ire["TIME"], gdp_ire["Value"], 'red', 'Ireland GDP Growth vs Irish Corporate Tax Rate', 'Year', 'GDP in millions USD', '')
ax2 = ax.twinx()
quickplot(ax2, gdp_ire["TIME"], gdp_ire["TaxRate"], 'blue', 'Ireland GDP Growth vs Irish Corporate Tax Rate', 'Year', 'Irish Tax Rate %', '')
ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
plt.show()


######### Ireland vs World Averages #########
# Dropping OECD, OECDE, EU28, EU27_2020, EA19 as these are sum totals of other countries & skew the numbers
for i in ['OECD', 'OECDE', 'EU28', 'EU27_2020', 'EA19']:
    gdp_data.drop(gdp_data[gdp_data['LOCATION'] == i].index, inplace=True)
    print(gdp_data.shape)

gdp_totals = gdp_data.pivot_table(values="Value", index="TIME", aggfunc=[np.sum, np.mean, np.median])
pd.options.display.float_format = '{:,.2f}'.format
print(gdp_totals)

gdp_ire.drop(gdp_ire[gdp_ire['TIME'] == 2020].index, inplace=True)
gdp_all = gdp_ire.merge(gdp_totals, on='TIME', suffixes=['_IRE', '_TOTALS'], how='left')
print(gdp_all)

fig, ax = plt.subplots()
# only the last of the common plotting factors (ie title & x,y labels) need be populated
quickplot(ax, gdp_all['TIME'], gdp_all['Value'], 'red', '', '', '', 'Ireland GDP')
quickplot(ax, gdp_all['TIME'], gdp_all[('median', 'Value')], 'blue', '', '', '', 'Median Total GDP')
quickplot(ax, gdp_all['TIME'], gdp_all[('mean', 'Value')], 'black', 'Ireland GDP vs Average GDP', 'Year', 'GDP in millions USD', 'Mean Total GDP')
ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
ax.legend()
plt.show()

gdp_all['Median_diffs'] = gdp_all[('median', 'Value')]-gdp_all['Value']
gdp_all['Median_diffs%']=gdp_all['Median_diffs']/gdp_all['Value']*100
print(gdp_all)

fig, ax = plt.subplots()
quickplot(ax, gdp_all['TIME'], gdp_all['Median_diffs%'], 'green', 'Ireland GDP vs Median GDP', 'Year', '% Diffs', 'Diffs to Median as % of IRL GDP')
ax.legend()
plt.show()
