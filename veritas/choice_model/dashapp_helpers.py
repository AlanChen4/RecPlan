import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from choice_model.choicemodel import ChoiceModel
from choice_model.constants import WAKE_BG_GEOJSON


def create_bubble_plot_fig(site_choice_visits):
    labels = list(site_choice_visits.keys())
    values = list(site_choice_visits.values())
    sizes = [site/1000 for site in values]

    bubble_fig = go.Figure(data=[go.Scatter(
        x=labels,
        y=values,
        marker_size=sizes,
        mode='markers'
    )])

    bubble_fig.update_layout(margin={'l': 20, 'r': 20, 'b': 5, 't': 5},)
    bubble_fig.update_yaxes(ticks="outside", ticklen=50)
    
    return bubble_fig


def create_map_scatter_plot_fig(visitation_prob, site_and_locations):
    site_location_and_prob = pd.merge(
        visitation_prob.mean(axis=1).to_frame(),
        site_and_locations,
        left_index=True, right_index=True
    )

    site_location_and_prob = site_location_and_prob.rename(columns={0: 'Visitation Probability'})
    site_location_and_prob = site_location_and_prob.reset_index()

    map_scatter_fig = px.scatter_mapbox(
        site_location_and_prob,
        lat='latitude', 
        lon='longitude', 
        color='Visitation Probability', 
        mapbox_style='open-street-map',
        size='Visitation Probability', 
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


def create_add_site_plot_fig():
    # calculate sum of equity for each block
    cm = ChoiceModel()
    bg_utility_black = cm.get_utility_by_block()[0].sum().to_frame()
    bg_utility_white = cm.get_utility_by_block()[1].sum().to_frame()

    # convert to format that can be read by choropleth mapbox
    bg_utility_black['GEOID'] = bg_utility_black.index.str.replace(', ', '').str[:6]
    bg_utility_black = bg_utility_black.rename(columns={0: 'black_utility'})

    fig = px.choropleth_mapbox(bg_utility_black, 
                               geojson=WAKE_BG_GEOJSON, 
                               locations='GEOID', 
                               color='black_utility', 
                               featureidkey='properties.GEOID',
                               color_continuous_scale="blugrn",
                               mapbox_style="carto-positron",
                               zoom=8, 
                               center={"lat": 35.7, "lon": -78.5},
                               opacity=0.8)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig
