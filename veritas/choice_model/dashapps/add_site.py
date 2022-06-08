import dash_bootstrap_components as dbc
import pandas as pd

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash


app = DjangoDash('AddSite', add_bootstrap_links=True)

app.layout = html.Div(id='output', children=[
    dbc.Label('(Please select site below and copy-paste this value into the GEOID field above)'),
    dbc.Input(id='geo_id', name='geoid', value='', disabled=True),
    dcc.Graph(id='add-site-plot', figure=None)
])

@app.callback(
    Output('geo_id', 'value'),
    [Input('add-site-plot', 'clickData')])
def update_figure(clickData):
    if clickData is not None:
        geo_id = clickData['points'][0]['location']
        return geo_id
