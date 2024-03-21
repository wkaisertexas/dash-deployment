#!/usr/bin/env python
# coding: utf-8

# ### Assignment #4: Basic UI
# 
# DS4003 | Spring 2024
# 
# Objective: Practice buidling basic UI components in Dash.
# 
# Task: Build an app that contains the following components user the gapminder dataset: `gdp_pcap.csv`. [Info](https://www.gapminder.org/gdp-per-capita/)
# 
# UI Components:
# 
# - A dropdown menu that allows the user to select `country`
# - The dropdown should allow the user to select multiple countries
# - The options should populate from the dataset (not be hard-coded)
# - A slider that allows the user to select `year`
# - The slider should allow the user to select a range of years
# - The range should be from the minimum year in the dataset to the maximum year in the dataset
# - A graph that displays the `gdpPercap` for the selected countries over the selected years
# - The graph should display the gdpPercap for each country as a line
# - Each country should have a unique color
# - Graph DOES NOT need to interact with dropdown or slider
# - The graph should have a title and axis labels in reader friendly format
# 
# Layout:
# 
# - Use a stylesheet
# - There should be a title at the top of the page
# - There should be a description of the data and app below the title (3-5 sentences)
# - The dropdown and slider should be side by side above the graph and take up the full width of the page
# - The graph should be below the dropdown and slider and take up the full width of the page
# 
# Submission:
# 
# - There should be only one app in your submitted work
# - Comment your code
# - Submit the html file of the notebook save as `DS4003_A4_LastName.html`
# 
# **For help you may use the web resources and pandas documentation. No co-pilot or ChatGPT.**
# 

# In[24]:


import pandas as pd
from dash import dcc, html, Input, Output, callback
import dash
import plotly.express as px
from datetime import datetime as dt


# # Reading in the data
# 
# Reads the `gdp_pcap.csv` file into a pandas dataframe.
# 
# After this, a minimal amount of exploratory data analysis is performed to understand the data's structure.
# 

# In[25]:


df = pd.read_csv("gdp_pcap.csv")  # csv to dataframe
df.head()


# In[26]:


# info about # of columns and # of rows
df.info()


# In[27]:


# describing the data: general increase over time in gdp
df.describe()


# # Data Processing
# 
# The goal of this section is to make a dataframe with columns: `country`, `year`, `gdp_per_cap`. Using this format is far easier in Plotly because I do not have to add multiple lines or do any weight filtering.
# 
# Getting the data into this format requires some weird hacks with pandas. The `melt` function was one that I learned about to un-pivot the data.
# 
# Furthermore, there was a tricky replace -> eval scenario to convert the `gdp_per_cap` to a float.
# 

# In[28]:


m_df = pd.melt(df, id_vars=["country"], var_name="year", value_name="gdp_per_cap")
m_df["year"] = m_df["year"].astype(int)  # year from str to int
m_df["gdp_per_cap"] = (
    m_df["gdp_per_cap"].replace({"k": "*1e3"}, regex=True).map(pd.eval).astype(float)
)  # EVIL EVAL HACKS
m_df


# # Making UI Components
# 
# We proceed by constructing three UI components for the dashboard:
# 
# - Header (title, countries and description)
# - Dropdown + Range Slider
# - Graph (updated later through a callback)
# 

# In[29]:


# Makes a HTMl with a header and a paragraph
header = [
    html.H1("GDP Per Capita By Country and Year"),
    html.P(
        f"""This dataset contains the GDP per capita of countries from {m_df['year'].min()} to {m_df['year'].max()}. GDP per capita is a measure of economic output per citizen. Roughly speaking, GDP per capita could be thought of as a measure of the goods produced by a society. A total of {m_df['country'].count()} are included in this dataset. Data was sourced from Gapminder which aggregated data and projections from Maddison project, the World Bank and the International Monetary Fund."""
    ),
]


# In[30]:


CURRENT_YEAR = dt.now().year  # the year of the current date

# makes a dropdown for the countries
country_dropdown = dcc.Dropdown(
    options=df["country"].unique(),  # unique countries
    multi=True,  # more than one selection
    id="country-dropdown",
    className="one-half column",  # required to be in a row
)

# makes a slider for the years
year_slider = dcc.RangeSlider(
    min=m_df.year.min(),
    max=m_df.year.max(),
    marks={
        1800: "1800",
        1900: "1900",
        2000: "2000",
        CURRENT_YEAR: str(CURRENT_YEAR),  # current year for context
        2100: "2100",
    },
    id="year-slider",
    className="one-half column",  # required to be in a row
)
# make the div a row
selectors = html.Div(
    [country_dropdown, year_slider], className="row"
)  # note: we learned how to do this in class, but I am just using css


# # Plotting the Data
# 
# This is a test plot to see the data before creating the dashboard and the callback.
# 

# In[31]:


# creates a multi-line plot using the melted dataframe
# fig = px.line(
#     m_df,
#     x="year",
#     y="gdp_per_cap",
#     color="country",  # allows many lines to be put there
#     title="Gross Domestic Product Per Capita By Country and Year",
# )
# fig.show()


# # Integrating UI Components
# 
# Taking the three UI components and integrating them into a Dash dashboard.
# 

# In[32]:


# Combining all the ui components
layout = [*header, selectors, dcc.Graph(id="gdp-per-cap-line-graph")]


# In[33]:


# callback which creates and updates the graph using the two inputs: year range and countries
# Note: this was not required, but I wanted to get some practice writing callbacks
@callback(
    Output(component_id="gdp-per-cap-line-graph", component_property="figure"),
    (
        Input(component_id="year-slider", component_property="value"),
        Input(component_id="country-dropdown", component_property="value"),
    ),
)
def update_graph(year_range: [int], countries: [str]) -> px.line:
    if countries is None:
        countries = m_df["country"].unique()  # use all countries if none are selected

    if year_range is None:
        year_range = [
            m_df["year"].min(),
            m_df["year"].max(),
        ]  # use all years if none are selected (should not happen)

    countries_mask = m_df["country"].isin(countries)  # mask for the countries
    year_mask = m_df["year"].between(year_range[0], year_range[1])  # mask for the year

    filtered_df = m_df[countries_mask & year_mask]  # combine the masks and filter

    fig = px.line(  # create the plot using the filtered dataframe. Use labels to rename the columns to make them more readable
        filtered_df,
        x="year",
        y="gdp_per_cap",
        color="country",
        labels={
            "year": "Year",
            "gdp_per_cap": "Gross Domestic Product (GDP) per Capita",
            "country": "Country",
        },
        title="Gross Domestic Product Per Capita By Country and Year",
    )
    return fig


# In[34]:


# stylesheet from the creator of dash which does nice things like adding class-based styling for containers
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(
    __name__, external_stylesheets=external_stylesheets
)  # creates a dash app with the name __main__
server = app.server  # required for deployment

# final app layout
app.layout = html.Div(
    layout, className="container"  # required to get the css row to work
)

if __name__ == "__main__":
    app.run_server(debug=True)  # runs the notebook

