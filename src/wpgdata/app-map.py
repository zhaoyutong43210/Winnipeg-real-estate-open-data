from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import pathlib

pwd = pathlib.Path().absolute().parent
fpath = pwd.parent / 'Winnipeg_real_estate_open_data/access_parcel' / 'Assessment_Parcels_cleaned.csv'
data = pd.read_csv(fpath)

app = Dash(__name__)

fig = px.scatter_mapbox(data, lat="Xcor", lon="Ycor", hover_name="Full Address", hover_data=["Total Living Area", "Total Assessed Value"],
                        color_discrete_sequence=["fuchsia"], zoom=3, height=300)

fig.update_layout(
    mapbox_style="white-bg",
    mapbox_layers=[
        {
            "below": 'traces',
            "sourcetype": "raster",
            "sourceattribution": "United States Geological Survey",
            "source": [
                "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
            ]
        },
        {
            "sourcetype": "raster",
            "sourceattribution": "Government of Canada",
            "source": ["https://geo.weather.gc.ca/geomet/?"
                       "SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&BBOX={bbox-epsg-3857}&CRS=EPSG:3857"
                       "&WIDTH=1000&HEIGHT=1000&LAYERS=RADAR_1KM_RDBR&TILED=true&FORMAT=image/png"],
        }
      ])
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()

app.layout = html.Div([
    html.H1(children='Winnipeg Real Estate Selling Data by year', style={'textAlign': 'center'}),
    dcc.Graph(figure = fig)
    ])




if __name__ == '__main__':
    app.run(debug=True)
