import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from choice_model.constants import WAKE_BG_GEOJSON


def create_bubble_plot_fig(visits):
    bubble_fig = px.scatter(
        x=visits.index,
        y=visits['visits'],
        size=visits['visits'],
        color=visits['type'],
    )
    bubble_fig.update_layout(margin={'l': 20, 'r': 20, 'b': 5, 't': 5}, height=700)
    bubble_fig.update_yaxes(ticks="outside", ticklen=50)
    
    return bubble_fig


def create_map_scatter_plot_fig(visits, site_and_locations):
    site_location_and_prob = pd.merge(
        visits,
        site_and_locations,
        left_index=True, right_index=True
    )

    site_location_and_prob = site_location_and_prob.rename(columns={'visits': 'Trips'})
    site_location_and_prob = site_location_and_prob.reset_index()

    map_scatter_fig = px.scatter_mapbox(
        site_location_and_prob,
        lat='latitude', 
        lon='longitude', 
        color='Trips', 
        mapbox_style='open-street-map',
        size='Trips', 
        hover_name='name'
    )
    map_scatter_fig.update_layout(margin={'l':0, 'r': 0, 't':0, 'b':0})

    return map_scatter_fig


def create_equity_evaluation_fig(black, other):
    equity_evaluation_fig = go.Figure([go.Bar(
        x=['Black', 'Other'],
        y=[black, other],
    )])
    equity_evaluation_fig.update_layout(margin={'l': 20, 'r': 20, 'b': 0, 't': 0},)

    return equity_evaluation_fig


def create_spatial_equity_fig(bg_utility_black):
    fig = px.choropleth_mapbox(
        bg_utility_black, 
        geojson=WAKE_BG_GEOJSON, 
        locations='GEOID', 
        color='black_utility', 
        featureidkey='properties.GEOID',
        color_continuous_scale="Bluered",
        mapbox_style="carto-positron",
        zoom=8, 
        center={"lat": 35.7, "lon": -78.5},
        opacity=0.8,
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_traces(marker_line_width=1)

    return fig
