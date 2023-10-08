import dash
from components import *

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

default_layout = html.Div(id="page",
                          children=[
                              dbc.Row([
                                  html.Div(style={'width': '470px', "margin": "20px 0px 0px 100px"},
                                           children=[
                                               html.Div(html.H2(id='text', children="Входные данные",
                                                                style={'text-align': 'center',
                                                                       "marginBottom": "20px"})),

                                               html.Div(style={'width': '450px',
                                                               "border": "2px black solid",
                                                               "marginTop": "10px",
                                                               "border-radius": "10px"},
                                                        id="input_div",
                                                        children=[asset_type, asset_list, futures_list, type_choice, price_field,
                                                                  strike_field, sigma_field, risk_free_field,
                                                                  date_field]),
                                               html.Div(figure),
                                               html.Div(button)]),

                                  html.Div(id="calculator_div",
                                           style={'width': '370px', "marginLeft": "10px", "marginTop": "32px"},
                                           children=[asian_fin, greeks_trees, board]),
                              ])
                          ], style={'height': '100%', 'width': '100%', 'max-width': '100%'})

app.layout = default_layout
app.title = "Опционный калькулятор"
app._favicon