# Import libraries
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pathlib
from app import app

# Get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()

# Read data
dfv = pd.read_csv(DATA_PATH.joinpath("used_cars_data_randomsample10000.csv"), sep="|")

# Get all the columns' types
col_types = dfv.dtypes

# Get continuous and categorical variables
categorical_vars = col_types[col_types == "object"].index
numerical_vars = col_types[col_types != "object"].index

# Define layout of Dashboard page
layout = html.Div([
    # Set title
    html.H1('US Used cars Dashboard', style={"textAlign": "center", "color":  "#4397a3", "font-weight": "bold"}),
    # Include dropdown for categorical variables
    html.Div([
        html.Div([
            html.Pre(children="Select from categorical variables:", style={"fontSize":"150%", "color":  "#BFBFBF"}),
            dcc.Dropdown(

                id='categ-dropdown', value='back_legroom', clearable=False,
                options=[{'label': x, 'value': x} for x in sorted(categorical_vars)],
                style={"backgroundColor": "#BFBFBF", "color": "#303030"}
            ),
            dcc.Graph(id='my-bar', figure={})
        ], className="six columns"),
    # Include dropdown for continuos variables
        html.Div([
            html.Pre(children="Select from continuous variables:", style={"fontSize":"150%", "color":  "#BFBFBF"}),
            dcc.Dropdown(
                id='conti-dropdown', value='city_fuel_economy', clearable=False,
                persistence=True, persistence_type='memory',
                options=[{'label': x, 'value': x} for x in numerical_vars],
                style={"backgroundColor": "#BFBFBF", "color": "#303030"}
            ),
            dcc.Graph(id='my-hist', figure={})
        ], className="six columns"),
    ], className="row")
])

# Define callback for categorical variables chart
@app.callback(
    Output(component_id='my-bar', component_property='figure'),
    [Input(component_id='categ-dropdown', component_property='value')]
)

# Define function to plot bar chart for categorical variables
def display_value(var_categ_chosen):
    group_df = pd.value_counts(dfv[var_categ_chosen]).to_frame().reset_index()
    group_df.columns = [var_categ_chosen, 'Count']
    fig = px.bar(group_df, x=var_categ_chosen, y="Count")
    fig = fig.update_layout({
        'paper_bgcolor': '#303030',
        'plot_bgcolor': '#303030',
        'font_color': "#BFBFBF"
    })

    fig = fig.update_traces(marker_color='#49c3d9', marker_line_color='#49c3d9')
    fig = fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#BFBFBF')
    fig = fig.update_xaxes(showline=True, linewidth=1, linecolor='#BFBFBF')
    return fig

# Define function to plot histogram chart for continuous variables
@app.callback(
    Output(component_id='my-hist', component_property='figure'),
    [Input(component_id='conti-dropdown', component_property='value')]
)
# Define function to plot bar chart for categorical variables
def display_value(var_cont_chosen):
    fig = px.histogram(dfv, x=var_cont_chosen)
    fig = fig.update_layout({
        'paper_bgcolor': '#303030',
        'plot_bgcolor': '#303030',
        'font_color': "#BFBFBF"
    })

    fig = fig.update_traces(marker_color='#49c3d9', marker_line_color='#49c3d9')
    fig = fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#BFBFBF')
    fig = fig.update_xaxes(showline=True, linewidth=1, linecolor='#BFBFBF')
    return fig