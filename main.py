import json
import pandas as pd
import streamlit as st
import plotly.express as px
from urllib.request import urlopen


with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# Imported Files:
positive = pd.read_csv("covid_confirmed_usafacts.csv")
deaths = pd.read_csv("covid_deaths_usafacts.csv")
population = pd.read_csv("covid_county_population_usafacts.csv")

# Cleaning up population Data
# Converting County Fips from int to string, then using zfill to make sure fips have 5 numbers
population['countyFIPS'] = population.countyFIPS.astype(str).str.zfill(5)
population = population.iloc[:, [0, 3]].set_index('countyFIPS')
population = population.drop(['00000'], axis=0)

# Cleaning data for Positive Cases (Line and Choropleth)
positive['countyFIPS'] = positive.countyFIPS.astype(str).str.zfill(5)
positive = positive.drop(['County Name', 'State', 'StateFIPS'], axis=1).set_index('countyFIPS')
positive.columns = pd.to_datetime(positive.columns)

# Cleaning data for Deaths (Line and Choropleth)
deaths['countyFIPS'] = deaths.countyFIPS.astype(str).str.zfill(5)
deaths = deaths.drop(['County Name', 'State', 'StateFIPS'], axis=1).set_index('countyFIPS')
deaths.columns = pd.to_datetime(deaths.columns)


# Function to check for full weeks only!
def drop_dates(df):
    drop_list = []
    # Transposed dataframe then used resample to check for incomplete weeks
    for i in df.T.resample('W-Sat'):
        # Incomplete weeks were added to drop list
        if len(i[1]) != 7:
            # print(i[0])
            drop_list.append(i[0])
    return drop_list


dates_to_drop = drop_dates(positive)
death_dates = drop_dates(deaths)
#print(dates_to_drop)
#print(death_dates)

# Question 1: Line plot of new COVID cases reported
positive = positive.reset_index()
positive_line = positive.drop(['countyFIPS'], axis=1)
# Convert headers to datetime
positive_line.columns = pd.to_datetime(positive_line.columns)
# Using resample to convert days to full weeks and summing values
positive_line = positive_line.resample('W-Sat', axis=1).sum()
# Dropping weeks that are not full using the drop list
positive_line = positive_line.drop(dates_to_drop, axis=1).T
# Creating new column for the sum of covid cases per week
positive_line['New_cases'] = positive_line.sum(axis=1)
positive_line = positive_line.iloc[:, -1]

# Using Streamlit to visualize line chart of New covid Cases
st.title("Covid Dashboard")
st.header('New Confirmed Covid Cases Per Week')
st.line_chart(positive_line)

# Question 2: Line plot of new COVID cases reported
deaths = deaths.reset_index()
deaths_line = deaths.drop(['countyFIPS'], axis=1)
deaths_line.columns = pd.to_datetime(deaths_line.columns)
deaths_line = deaths_line.resample('W-Sat', axis=1).sum()
deaths_line = deaths_line.drop(dates_to_drop, axis=1).T
deaths_line['New_cases'] = deaths_line.sum(axis=1)
deaths_line = deaths_line.iloc[:, -1]
st.header('Covid Deaths Per Week')
st.line_chart(deaths_line)

# # Question 3
# Setting County Fips as index
positive = positive.set_index('countyFIPS')
# Dropping fips that are unallocated
positive = positive.drop(['00000'], axis=0)
# Converting headers to datetime
positive.columns = pd.to_datetime(positive.columns)
# Using resample to convert days to full weeks (Sun-Sat) anc calculated the mean
Choropleth_positive = positive.resample('W-Sat', axis=1).mean()
# Using drop list to drop incomplete weeks
Choropleth_positive = Choropleth_positive.drop(dates_to_drop, axis=1)
# Using div() function to divide the mean of each week by the population size to get per 100,000
Choropleth_positive = Choropleth_positive.div(population.iloc[:, -1], axis='rows').multiply(100000).reset_index()
Choropleth_positive.columns = Choropleth_positive.columns.astype(str)
# Used melt to convert convert dataframe into two columns (variable and value)
Choropleth_positive = pd.melt(Choropleth_positive, id_vars=['countyFIPS'])
# Using plotly express choropleth, plotted per 100,000 cases with an animation that runs through all the weeks
fig = px.choropleth(Choropleth_positive, geojson=counties, locations='countyFIPS',
                    color='value',
                    color_continuous_scale="Viridis",
                    range_color=(0, 50000),
                    animation_frame='variable',
                    scope="usa",
                    labels={'countyFIPS': 'Fips'})
fig.show()
# Adding Choropleth to dashboard
# (Warning: Streamlit has a lit of 200MB, this data is larger and will produce an error)
#st.plotly_chart(fig)

# # Question 4: Average Deaths per 100,000 in a week
# deaths = deaths.set_index('countyFIPS')
# # Dropping fips that are unallocated
# deaths = deaths.drop(['00000'], axis=0)
# # Converting headers to datetime
# deaths.columns = pd.to_datetime(deaths.columns)
# # Using resample to convert days to full weeks (Sun-Sat) anc calculated the mean
# Choropleth_deaths = deaths.resample('W-Sat', axis=1).mean()
# # Using drop list to drop incomplete weeks
# Choropleth_deaths = Choropleth_deaths.drop(death_dates, axis=1)
# # Using div() function to divide the mean of each week by the population size to get per 100,000
# Choropleth_deaths = Choropleth_deaths.div(population.iloc[:, -1], axis='rows').multiply(100000).reset_index()
# Choropleth_deaths.columns = Choropleth_deaths.columns.astype(str)
# # Used melt to convert convert dataframe into two columns (variable and value)
# Choropleth_deaths = pd.melt(Choropleth_deaths, id_vars=['countyFIPS'])
# # Using plotly express choropleth, plotted per 100,000 cases with an animation that runs through all the weeks
# fig1 = px.choropleth(Choropleth_deaths, geojson=counties, locations='countyFIPS',
#                      color='value',
#                      color_continuous_scale="Viridis",
#                      range_color=(0, 1000),
#                      animation_frame='variable',
#                      scope="usa",
#                      labels={'countyFIPS': 'Fips'})
# fig1.show()

# Adding Choropleth to dashboard
# (Warning: Streamlit has a lit of 200MB, this data is larger and will produce an error)
# st.plotly_chart(fig1)
