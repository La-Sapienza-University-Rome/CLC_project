# Import libraries
import base64
import datetime
import io
import json
import numpy as np

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import pandas as pd
from app import app

import boto3
import smart_open

import pathlib

# Delete
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()

# Define layout for web page "upload"
layout = html.Div([
    html.H1('Car Price Predictor', style={"textAlign": "center", "color":  "#4397a3", "font-weight": "bold"}),
    # Set title
    html.H1('Upload new data set', style={"textAlign": "center", "color":  "#4397a3", "font-weight": "bold"}),
    # Set text for uploading
    html.Pre(children="Select the file to upload (must be a CSV file, separated by '|'):", style={"fontSize":"150%", "color":  "#BFBFBF"}),
    dcc.Upload(
    # Set uploading button
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px',
            'borderColor': '#BFBFBF'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])



# Define function to upload CSV (must be separated by "|")
def parse_contents(contents, filename, date):
    
    # Conncet to S3
    try:
        #s3 = boto3.resource('s3')
        #model_file = s3.Object('clc-prediction-bucket','model_lin_reg.txt').get()['Body'] # .read().decode('utf-8')
        model_path = 's3:clc-prediction-bucket/weights.txt'
        model_f = smart_open.open(model_path, 'r')
        #model_f = smart_open.open(DATA_PATH.joinpath("weights.txt"), 'r')
        #h1 = html.H1(model_f.readline(), style={"textAlign": "center", "color":  "#4397a3", "font-weight": "bold"})
        model_f = model_f.readline()
        json_acceptable_string = model_f.replace("'", "\"")
        d = json.loads(json_acceptable_string)
        w = np.array(d['weights'])
        #model_f.close()
    except Exception as e:
        h1 = html.H1(str(e), style={"textAlign": "center", "color":  "#4397a3", "font-weight": "bold"})
    
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), index_col=0)
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    df_np=np.array(df)
    x = list(np.around(w[0]+np.matmul(w[1:], np.transpose(df_np)), 1))
    cars_list = ['car_'+ str(i)  for i in range(1, len(x)+1)] 
    df_res = pd.DataFrame(columns=['Car', 'Prediction'])
    df_res.Car=cars_list
    df_res.Prediction=x
    # Return (print) the complete table uploaded
    return html.Div([
        # Write name of the file uploaded
        html.H5("Data set name: "),html.H5(filename),html.Br(),
        # Write time of the uploading
        html.H5("Uploading time: "),html.H5(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {'name': i, 'id': i, 'deletable': True, 'selectable': True} for i in df_res.columns
        ],
        data=df_res.to_dict('records'),
        editable=True,
        style_header={'backgroundColor': 'rgb(30, 30, 30)'},
        style_cell={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
        },
        #filter_action='native',
        sort_action='native',
        sort_mode='multi',
        column_selectable='single',
        row_selectable='multi',
        row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action='native',
        page_current=0,
        page_size=10,
        fill_width=False
    ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

# Call back to retrieve information after clicking in the upload button
@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children
