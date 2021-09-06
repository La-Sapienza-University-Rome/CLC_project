# Import libraries
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app
from app import server

# Connect to your app pages
from apps import dashboard, upload

# Define application layout (including links to both pages)
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        html.H5(dcc.Link('Dashboard    |', href='/apps/dashboard')),
        html.H5(dcc.Link('    Upload', href='/apps/upload')),
    ], className="row"),
    html.Div(id='page-content', children=[])
])

# Set navigation inside of pages
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/dashboard':
        return dashboard.layout
    if pathname == '/apps/upload':
        return upload.layout
    else:
        return dashboard.layout


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8080)
