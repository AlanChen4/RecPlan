import dash_bootstrap_components as dbc
import pandas as pd

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from django_plotly_dash import DjangoDash
from django.urls import reverse_lazy

from choice_model.models import ModifiedSite, ModifiedSitesBundle

GRAPH_STYLE = {
    'width': '90vw'
}

app = DjangoDash('AddSite',
    add_bootstrap_links=True
)

app.layout = html.Div(id='output', className="container mt-5", children=[
    html.Form([
        html.H3("Add a New Site"),
        dbc.Input(type='hidden', id='csrfmiddlewaretoken', value=None, name='csrfmiddlewaretoken'),
        dbc.Input(type='hidden', id='bundle_id', value=None, name='bundle_id'),
        dbc.Row([
            dbc.Col([
                dbc.Label('Site Name'),
                dbc.Input(id='site_name', name='site_name', value='')
            ], className='col-md-5'),
            dbc.Col([
                dbc.Label('Acres'),
                dbc.Input(id='acres', name='acres', value=0)
            ], className='col-md-2'),
            dbc.Col([
                dbc.Label('Selected Block'),
                dbc.Input(id='geoid', name='geoid', value='')
            ], className='col-md-5'),
        ], className='my-2'),
        dbc.Row([
            dbc.Col([
                dbc.Label('Trails'),
                dbc.Input(id='trails', name='trails', type='number', value=0),
            ], className='col-md-4'),
            dbc.Col([
                dbc.Label('Trail Miles'),
                dbc.Input(id='trail_miles', name='trail_miles', type='number', value=0),
            ], className='col-md-4'),
            dbc.Col([
                dbc.Label('Bathrooms'),
                dbc.Input(id='bathrooms', name='bathrooms', type='number', value=0),
            ], className='col-md-4'),
        ], className='my-2'),
        dbc.Row([
            dbc.Col([
                dbc.Label('Picnic Area'),
                dbc.RadioItems(id='picnic_area', options=[
                    {'label': 'Yes', 'value': 1},
                    {'label': 'No', 'value': 0},
                ], className='form-check-inline', name='picnic_area', value=1)
            ], className='col-md-4'),
            dbc.Col([
                dbc.Label('Sports Facilities'),
                dbc.RadioItems(id='sports_facilities', options=[
                    {'label': 'Yes', 'value': 1},
                    {'label': 'No', 'value': 0},
                ], className='form-check-inline', name='sports_facilities', value=1)
            ], className='col-md-4'),
            dbc.Col([
                dbc.Label('Swimming Facilities'),
                dbc.RadioItems(id='swimming_facilities', options=[
                    {'label': 'Yes', 'value': 1},
                    {'label': 'No', 'value': 0},
                ], className='form-check-inline', name='swimming_facilities', value=1)
            ], className='col-md-4'),
        ], className='my-2'),
        dbc.Row([
            dbc.Col([
                dbc.Label('Boat Launch'),
                dbc.RadioItems(id='boat_launch', options=[
                    {'label': 'Yes', 'value': 1},
                    {'label': 'No', 'value': 0},
                ], className='form-check-inline', name='boat_launch', value=1)
            ], className='col-md-4'),
            dbc.Col([
                dbc.Label('Waterbody'),
                dbc.RadioItems(id='waterbody', options=[
                    {'label': 'Yes', 'value': 1},
                    {'label': 'No', 'value': 0},
                ], className='form-check-inline', name='waterbody', value=1)
            ], className='col-md-4'),
            dbc.Col([
                dbc.Label('Playgrounds'),
                dbc.RadioItems(id='playgrounds', options=[
                    {'label': 'Yes', 'value': 1},
                    {'label': 'No', 'value': 0},
                ], className='form-check-inline', name='playgrounds', value=1)
            ], className='col-md-4'),
        ], className='my-2'),
        dbc.Row([
            html.Button('Create New Site', type='submit', id='submit-btn', className='btn btn-outline-primary', form='site-form', formMethod='POST', formAction='/site/dash/')
        ], className='m-2'),
        dbc.Row([
            dcc.Graph(id='add-site-plot', figure=None, style=GRAPH_STYLE)
        ], className='mx-2'),
        html.Div(id="hidden-div-for-redirect"),
    ], id='site-form', className='mx-4'),
])

@app.callback(
    Output('geoid', 'value'),
    [Input('add-site-plot', 'clickData')])
def update_figure(clickData):
    if clickData is not None:
        geo_id = clickData['points'][0]['location']
        return geo_id

@app.callback(
    Output('hidden-div-for-redirect', 'children'),
    Input('submit-btn', 'n_clicks'), 
    Input('bundle_id', 'value'), 
)
def redirect(clickData, bundle_id):
    if clickData is not None:
        return dcc.Location(id='redirect', pathname=f'/model/{bundle_id}/update/')
