import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash


app = DjangoDash('SiteChoiceProb', add_bootstrap_links=True)

graph_style = {
    'height': '50%',
    'display': 'none',
}

app.layout = html.Div(children=[
    dcc.Checklist(
        id='checklist', 
        options=[
            {'label': 'Bubble Plot', 'value': 'bubble-plot'},
            {'label': 'Map Scatter Plot', 'value': 'map-scatter-plot'},
        ],
        value='bubble-plot',
        style={'font-family': "sans-serif"}
    ),
    dcc.Graph(id='bubble-plot', figure=None, style=graph_style),
    dcc.Graph(id='map-scatter-plot', figure=None, style=graph_style),
])

@app.callback(
    Output('bubble-plot', 'style'),
    Input('checklist', 'value')
)
def display_graphs(selected_values):
    if 'bubble-plot' in selected_values:
        return {'display': 'block'}
    return {'display': 'none'}


@app.callback(
    Output('map-scatter-plot', 'style'),
    Input('checklist', 'value')
)
def display_graphs(selected_values):
    if 'map-scatter-plot' in selected_values:
        return {'display': 'block'}
    return {'display': 'none'}
