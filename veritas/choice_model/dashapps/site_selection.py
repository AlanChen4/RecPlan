from dash import dcc, html
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash


app = DjangoDash('SiteSelection')

app.layout = html.Div(children=[
    dcc.Graph(id='map-plot', figure=None)
])
