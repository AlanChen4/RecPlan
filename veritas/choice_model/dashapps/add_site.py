import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash


app = DjangoDash('AddSite')

app.layout = html.Div(children=[
    dcc.Graph(id='add-site-plot', figure=None)
])
