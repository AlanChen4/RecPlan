import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash


app = DjangoDash('SiteSelection', add_bootstrap_links=True)

app.layout = html.Div(children=[
    dcc.Graph(id='map-plot', figure=None)
])
