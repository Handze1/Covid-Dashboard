import json
from urllib.request import urlopen
import pandas as pd
import streamlit as st
import plotly.express as px



with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)


def read_csv_pop(file):
    """
    Reading in CSV file for population data
    Cleaning up population Data
    Converting County Fips from int to string, then using zfill to make sure fips have 5 numbers
    """
    df_pop = pd.read_csv(file)
    df_pop['countyFIPS'] = df_pop.countyFIPS.astype(str).str.zfill(5)
    df_pop = df_pop.iloc[:, [0, 3]].set_index('countyFIPS')
    df_pop = df_pop.drop(['00000'], axis=0)
    return df_pop


def read_csv_cases(file):
    """
    Reading in CSV files for confirmed cases and covid deaths
    """
    df_read = pd.read_csv(file)
    df_read['countyFIPS'] = df_read.countyFIPS.astype(str).str.zfill(5)
    df_read = df_read.drop(['County Name', 'State', 'StateFIPS'], axis=1).set_index('countyFIPS')
    df_read.columns = pd.to_datetime(df_read.columns)
    return df_read


def drop_dates(df):
    """
    Function to check for full weeks only
    Transposed dataframe then used resample to check for incomplete weeks
    Incomplete weeks were added to drop list
    """
    drop_list = []
    for i in df.T.resample('W-Sat'):
        if len(i[1]) != 7:
            drop_list.append(i[0])
    return drop_list


def lineplot_clean_data(df):
    """
    Convert headers to datetime
    Using resample to convert days to full weeks and summing values
    Dropping weeks that are not full using the drop list
    Creating new column for the sum of covid cases/deaths per week
    """
    df = df.reset_index().drop(['countyFIPS'], axis=1)
    df.columns = pd.to_datetime(df.columns)
    df = df.resample('W-Sat', axis=1).sum().drop(dates_to_drop, axis=1).T
    df['New_Cases'] = df.sum(axis=1)
    clean_data_for_vis = df.iloc[:, -1]
    return clean_data_for_vis


def choropleth_clean_data(df):
    """
    Dropping fips that are unallocated
    Converting headers to datetime
    Using resample to convert days to full weeks (Sun-Sat) anc calculated the mean
    Using drop list to drop incomplete weeks
    Using div() function to divide the mean of each week by the population size to get per 100,000
    Used melt to convert convert dataframe into two columns (variable and value)

    """
    df = df.reset_index()
    df = df.set_index('countyFIPS')
    df = df.drop(['00000'], axis=0)
    df.columns = pd.to_datetime(df.columns)
    df = df.resample('W-Sat', axis=1).mean()
    df = df.drop(dates_to_drop, axis=1)
    df = df.div(population.iloc[:, -1], axis='rows').multiply(100000).reset_index()
    df.columns = df.columns.astype(str)
    df = pd.melt(df, id_vars=['countyFIPS'])
    return df

def line_plot_vis(df):
    """
    Lineplot Visualization Using Streamlit
    """
    df = lineplot_clean_data(df)
    st.line_chart(df)
    return

# 
def choropleth_confirmed_vis(df):
    """
    Choropleth Visualization Using Plotly
    Using plotly express choropleth, plotted per 100,000 cases with an animation that runs through all the weeks
    """
    fig = px.choropleth(df, geojson=counties, locations='countyFIPS',
                    color='value',
                    color_continuous_scale="Viridis",
                    range_color=(0, 50000),
                    animation_frame='variable',
                    scope="usa",
                    labels={'countyFIPS': 'Fips'})
    fig.show()
    return fig


def choropleth_deaths_vis(df):
    """
    Choropleth Visualization Using Plotly
    Using plotly express choropleth, plotted per 100,000 cases with an animation that runs through all the weeks
    """
    fig = px.choropleth(df, geojson=counties, locations='countyFIPS',
                    color='value',
                    color_continuous_scale="Viridis",
                    range_color=(0, 2000),
                    animation_frame='variable',
                    scope="usa",
                    labels={'countyFIPS': 'Fips'})
    fig.show()
    return fig

# Adding Choropleth to dashboard
# (Warning: Streamlit has a lit of 200MB, this data is larger and will produce an error)
#st.plotly_chart(fig)


if __name__ == "__main__":
    st.title("Covid Dashboard")
    positive = read_csv_cases("covid_confirmed_usafacts.csv")
    dates_to_drop = drop_dates(positive)
    st.header('Confirmed Covid Cases Per Week')
    confirmed_cases_vis = line_plot_vis(positive)
    deaths = read_csv_cases("covid_deaths_usafacts.csv")
    dates_to_drop = drop_dates(deaths)
    st.header('Confirmed Covid Deaths Per Week')
    confirmed_deaths_vis = line_plot_vis(deaths)
    population = read_csv_pop("covid_county_population_usafacts.csv")
    choro_confirm = choropleth_clean_data(positive)
    choro_deaths = choropleth_clean_data(deaths)
    #choropleth_confirmed_vis(choro_confirm) # Takes a very long time to run
    #choropleth_deaths_vis(choro_deaths) # Takes a very long time to run
    