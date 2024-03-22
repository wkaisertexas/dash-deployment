#!/usr/bin/env python
# coding: utf-8


"""

Note: if you are grading this, you should check out 

assignment5_william_kaiser.ipynb  

which is the jupyter notebook version of this code.

The Python script created from the notebook is below.

"""

# ### Assignment #5: Callbacks
# 
# DS4003 | Spring 2024
# 
# Objective: Practice building basic UI components in Dash. 
# 
# Task: Build an app that contains the following components user the gapminder dataset: `gdp_pcap.csv`. [Info](https://www.gapminder.org/gdp-per-capita/)
# 
# UI Components:
# x- A dropdown menu that allows the user to select `country`
# x -   The dropdown should allow the user to select multiple countries
# x -   The options should populate from the dataset (not be hard-coded)
# x - A slider that allows the user to select `year`
# x -   The slider should allow the user to select a range of years
# x -   The range should be from the minimum year in the dataset to the maximum year in the dataset
# x - A graph that displays the `gdpPercap` for the selected countries over the selected years
# x -   The graph should display the gdpPercap for each country as a line
# x -   Each country should have a unique color
# x -   Graph DOES NOT need to interact with dropdown or slider
# x -   The graph should have a title and axis labels in reader friendly format  
# 
# Layout:  
# x - Use a stylesheet
# x - There should be a title at the top of the page
# x - There should be a description of the data and app below the title (3-5 sentences)
# x - The dropdown and slider should be side by side above the graph and take up the full width of the page
# x - The graph should be below the dropdown and slider and take up the full width of the page
# 
# Submission: 
# - There should be only one app in your submitted work
# - Comment your code
# - Submit the html file of the notebook save as `DS4003_A4_LastName.html`
# 
# 
# **For help you may use the web resources and pandas documentation. No co-pilot or ChatGPT.**

# In[14]:


# imports 
import pandas as pd
from dash import dcc, html, Input, Output, callback
import dash
import plotly.express as px


# # Reading in the data

# In[15]:


# reading in the data
df = pd.read_csv('gdp_pcap.csv')
df.head()


# In[16]:


df.info() # getting some basic info about the data


# In[17]:


df.describe() # using the describe function to get averages


# # Data Processing
# 
# The goal of this section is to make a dataframe with columns: `country`, `year`, `gdp_per_cap`. Using this format is far easier in Plotly because I do not have to add multiple lines or do any weight filtering. 
# 
# Getting the data into this format requires some weird hacks with pandas. The `melt` function was one that I learned about to un-pivot the data. Furthermore, there was a tricky replace -> eval scenario to convert the gdp_per_cap to a float. 

# In[18]:


# using the melt function to get the data into the right format
m_df = pd.melt(df, id_vars=['country'], var_name='year', value_name='gdp_per_cap')
m_df['year'] = m_df['year'].astype(int)
m_df['gdp_per_cap'] = m_df['gdp_per_cap'].replace({'k': '*1e3'}, regex=True).map(pd.eval).astype(float) # EVIL EVAL HACKS :-> I did not have to do this because I think plotly does it for you
m_df # showing the preview


# # Making UI Components

# In[19]:


# making the number of countries
num_countries = len(m_df['country'].unique())
header = [
  html.H1('GDP Per Capita By Country and Year'),
  html.P(f"""This dataset contains the GDP per capita of countries from {m_df['year'].min()} to {m_df['year'].max()}. GDP per capita is a measure of economic output per citizen. Roughly speaking, GDP per capita could be thought of as a measure of the goods produced by a society. A total of {num_countries} are included in this dataset. """),
  html.P(f"Countries: {', '.join(m_df['country'].unique())}"),
]


# In[20]:

# creating a dropdown of countries
country_dropdown = dcc.Dropdown(
  options=df['country'].unique().tolist(),
  multi=True,
  id='country-dropdown',
  className='one-half column',
)

# creating a range slider with well-defined years
year_slider = dcc.RangeSlider(
    m_df.year.min(),
    m_df.year.max(),
    marks={
        1800: '1800',
        1900: '1900',
        2000: '2000',
        2020: '\'20',
        2100: '2100'
    },
    id='year-slider', 
    className='one-half column',
)

# labels = html.Div([html.Label("Country Selector"), html.Label("Year Range Selector")], className='row', style={'display': 'flex', 'justify-content': 'space-between'})
# make the div a row
selectors = html.Div([country_dropdown, year_slider], className='row') # note: we learned how to do this in class, but I am just using css

# selectors = html.Div([labels, selectors], className='container')

# # Plotting the Data

# In[21]:

# making a simple plot to show the data inside the notebook
fig = px.line(m_df, x="year", y="gdp_per_cap", color='country', title='Gross Domestic Product Per Capita By Country and Year')
# fig.show()


# # Integrating UI Components

# In[22]:


# making the layout
layout = [
  *header,
  selectors,
  dcc.Graph(id='gdp-per-cap-line-graph')
]


# In[25]:


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = [ f"rgb({i}, {i}, {i})" for i in range(1, 256) ]

@callback(
    Output(component_id="gdp-per-cap-line-graph", component_property="figure"),
    (Input(component_id="year-slider", component_property="value"), Input(component_id="country-dropdown", component_property="value"))
)
def update_graph(year_range: [int], countries: [str]):

    if countries is None: # Setting default values
        countries = m_df['country'].unique()

    if year_range is None: # setting default values
        year_range = [m_df['year'].min(), m_df['year'].max()]

    # making a map of valid countries
    countries_mask = m_df['country'].isin(countries)
    year_mask = m_df['year'].between(year_range[0], year_range[1])

    filtered_df = m_df[countries_mask & year_mask]

    fig = px.line(filtered_df, x="year", y="gdp_per_cap", color='country', labels={
                     "year": "Year",
                     "gdp_per_cap": "Gross Domestic Product (GDP) per Capita",
                     "country": "Country",
                 },              color_discrete_sequence=colors,title="Gross Domestic Product Per Capita By Country and Year")
    return fig

app.layout = html.Div(layout, className='container')
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)

