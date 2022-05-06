import dash_bootstrap_components as dbc
import pandas as pd

from dash import dcc, html
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

app.layout = html.Div(id='output', children=[
    dbc.Form([
        dbc.Row([
            dbc.Col([
                dbc.Label('Site Name'),
                dbc.Input(id='site_name', value='')
            ], class_name='col-md-5'),
            dbc.Col([
                dbc.Label('Acres'),
                dbc.Input(id='acres', value=0)
            ], class_name='col-md-2'),
            dbc.Col([
                dbc.Label('Selected Block'),
                dbc.Input(id='geoid', disabled=True, value='')
            ], class_name='col-md-5'),
        ], class_name='my-2'),
        dbc.Row([
            dbc.Col([
                dbc.Label('Trails'),
                dbc.Input(id='trails', type='number', value=0),
            ], class_name='col-md-4'),
            dbc.Col([
                dbc.Label('Trail Miles'),
                dbc.Input(id='trail_miles', type='number', value=0),
            ], class_name='col-md-4'),
            dbc.Col([
                dbc.Label('Bathrooms'),
                dbc.Input(id='bathrooms', type='number', value=0),
            ], class_name='col-md-4'),
        ], class_name='my-2'),
        dbc.Row([
            dbc.Col([
                dbc.Label('Picnic Area'),
                dbc.RadioItems(id='picnic_area', options=[
                    {'label': 'Yes', 'value': 1},
                    {'label': 'No', 'value': 0},
                ], class_name='form-check-inline', value=1)
            ], class_name='col-md-4'),
            dbc.Col([
                dbc.Label('Sports Facilities'),
                dbc.RadioItems(id='sports_facilities', options=[
                    {'label': 'Yes', 'value': 1},
                    {'label': 'No', 'value': 0},
                ], class_name='form-check-inline', value=1)
            ], class_name='col-md-4'),
            dbc.Col([
                dbc.Label('Swimming Facilities'),
                dbc.RadioItems(id='swimming_facilities', options=[
                    {'label': 'Yes', 'value': 1},
                    {'label': 'No', 'value': 0},
                ], class_name='form-check-inline', value=1)
            ], class_name='col-md-4'),
        ], class_name='my-2'),
        dbc.Row([
            dbc.Col([
                dbc.Label('Boat Launch'),
                dbc.RadioItems(id='boat_launch', options=[
                    {'label': 'Yes', 'value': 1},
                    {'label': 'No', 'value': 0},
                ], class_name='form-check-inline', value=1)
            ], class_name='col-md-4'),
            dbc.Col([
                dbc.Label('Waterbody'),
                dbc.RadioItems(id='waterbody', options=[
                    {'label': 'Yes', 'value': 1},
                    {'label': 'No', 'value': 0},
                ], class_name='form-check-inline', value=1)
            ], class_name='col-md-4'),
            dbc.Col([
                dbc.Label('Playgrounds'),
                dbc.RadioItems(id='playgrounds', options=[
                    {'label': 'Yes', 'value': 1},
                    {'label': 'No', 'value': 0},
                ], class_name='form-check-inline', value=1)
            ], class_name='col-md-4'),
        ], class_name='my-2'),
        dbc.Row([
            dcc.Link(dbc.Button('Create New Site'), href='/', refresh=True)
        ], class_name='m-2'),
        dbc.Row([
            dcc.Graph(id='add-site-plot', figure=None, style=GRAPH_STYLE)
        ], class_name='mx-2'),
        html.Div(id='slug', className='d-none'),
    ], id='form', class_name='mx-4'),
])

@app.callback(
    Output('geoid', 'value'),
    [Input('add-site-plot', 'clickData')])
def update_figure(clickData):
    if clickData is not None:
        geo_id = clickData['points'][0]['location']
        return geo_id

@app.callback(
    Output('output', 'children'),
    Input('form', 'n_submit'),
    State('site_name', 'value'),
    State('geoid', 'value'),
    State('acres', 'value'),
    State('trails', 'value'),
    State('trail_miles', 'value'),
    State('picnic_area', 'value'),
    State('sports_facilities', 'value'),
    State('swimming_facilities', 'value'),
    State('boat_launch', 'value'),
    State('waterbody', 'value'),
    State('bathrooms', 'value'),
    State('playgrounds', 'value'),
    State('slug', 'children'),
    prevent_initial_call=True
)
def handle_submit(n_submit, site_name, geoid, acres, trails, trail_miles, 
                 picnic_area, sports_facilities, swimming_facilities, 
                 boat_launch, waterbody, bathrooms, playgrounds, slug):
    
    bundle = ModifiedSitesBundle.objects.filter(bundle_id=slug)
    if bundle.exists():
        bg = pd.read_parquet('./choice_model/data/distances.parquet').columns
        for x_geoid, latitude, longitude in zip(bg.str.replace(', ','').str[:6], bg.str.split(', ').str[2], bg.str.split(', ').str[3]):
            if x_geoid == geoid:
                ModifiedSite.objects.create(
                    name=site_name,
                    bundle_id=bundle.get(bundle_id=slug),
                    latitude=latitude,
                    longitude=longitude,
                    acres=acres,
                    trails=trails,
                    trail_miles=trail_miles,
                    picnic_area=picnic_area,
                    sports_facilities=sports_facilities,
                    swimming_facilities=swimming_facilities,
                    boat_launch=boat_launch,
                    waterbody=waterbody,
                    bathrooms=bathrooms,
                    playgrounds=playgrounds,
                )
                return None
    else:
        print("Could not find bundle")