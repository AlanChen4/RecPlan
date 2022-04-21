import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash


app = DjangoDash('AddSite')

app.layout = html.Div(children=[
    dcc.Graph(id='add-site-plot', figure=None)
])

@app.callback(
    Output('add-site-plot', 'figure'),
    [Input('add-site-plot', 'clickData')])
def update_figure(clickData):
    if clickData is not None:
        geo_id = clickData['points'][0]['location']
        print(geo_id)