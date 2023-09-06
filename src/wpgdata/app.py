from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

df = pd.read_csv('~/htmls/Winnipeg-real-estate-open-data/Winnipeg_real_estate_open_data/combined_data.csv')

# clean up the sale price
df['Sale Price'] = df['Sale Price'].str.replace('$', '')
df['Sale Price'] = df['Sale Price'].str.replace(',', '')
df['Sale Price'] = df['Sale Price'].astype(float)

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='Winnipeg Real Estate Selling Data by year', style={'textAlign': 'center'}),
    dcc.Dropdown(df.loc[:, "Sale Year"].unique(), '2012', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
])

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df[df.loc[:, "Sale Year"] == value]
    # if value2:

    return px.histogram(dff, x='Sale Price')

if __name__ == '__main__':
    app.run(debug=True)
