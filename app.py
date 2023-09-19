import dash
from dash import Input, Output, dash_table
from dash import dcc
from dash import html
from datetime import date
from back import Option
import numpy as np
import pandas as pd
import datetime
import dash_bootstrap_components as dbc

data = [['Стоимость опциона', '', ''], ['Дельта', '', ''], ['Гамма', '', ''], ['Вега', '', ''], ['Тета', '', ''], ['Ро', '', '']]
blank = pd.DataFrame(data, columns=[' ', "Колл", "Пут"])

app = dash.Dash(__name__)

app.layout = html.Div(id="page", children=(html.Div(id="input_cells", children=(html.H1(id='text', children = "Ввод"),
                                html.Div(id='dropdowns', children=(dcc.Dropdown(id='asset_list', options=["ABMN", "AMZN"], placeholder='Наименование актива', style = {"marginTop" : "20px", "width" : "317px"}))),
                                html.Div([dcc.RadioItems(id='type_choice', options=['Европейский', 'Американский'], inline=True)], style = {"margin" : "10px 0px 0px 40px"}),
                                html.Div([dcc.Input(id='price_field', value=100, type='number', placeholder='Цена актива', style= {"width": "308px","marginTop" : "10px"})]),
                                html.Div([dcc.Input(id='strike_field', value=100, type='number', placeholder='Цена исполнения', style= {"width": "308px","marginTop" : "10px"})]),
                                html.Div([dcc.Input(id='sigma_field', value=10, type='number', placeholder='Волатильность, %', style= {"width": "308px","marginTop" : "10px"})]),
                                html.Div([dcc.Input(id='risk_free_field', value=10, type='number', placeholder='Безрисковая ставка, %', style= {"width": "308px","marginTop" : "10px"})]),
                                html.Div([dcc.DatePickerRange(id='start_date_field', clearable=True, display_format='D.M.Y',start_date=date(2024,12,12), end_date=date(2024, 12, 12), style= {"width": "500px","marginTop" : "10px"})]),
                                html.Div([dcc.Input(id='number_of_steps', type='text', placeholder='Количество шагов дерева', style= {"width": "200px","marginTop" : "10px"})])), style={'display':'inline-block'}),
                      
                      html.Div(id="calculator_div", children=(html.Div(id='results', children=(html.Div(id='put_part', children=(html.H1(id='calculated', children='Результаты'), html.Div(id='table_update', children=dash_table.DataTable(blank.to_dict('records'), [{"name": i, "id": i} for i in blank.columns], id='greeks', style_header={'backgroundColor': 'red','fontWeight': 'bold'}, style_as_list_view=True))), style={'display':'inline-block'})), style={'display' : 'flex'})),
                               style={'display':'inline-block', 'width':'19%'})), style={'display':'flex'})


@app.callback(Output("dropdowns", "children"), Input("asset_list", "value"))
def get_attributes(asset):

    if asset!=None:
        return (dcc.Dropdown(id='asset_list', options=["ABMN", "AMZN"], value=asset, placeholder='Наименование актива', style={"marginTop": "20px", "width": "317px"}),
                dcc.Dropdown(id='stock_future_list',
                             options=["Фьючерсы", "Акции", None],
                             value='string',
                             placeholder='Тип базового актива',
                             style={"marginTop": "20px", "width": "317px"}))
    return (dcc.Dropdown(id='asset_list',
                         options=["ABMN", "AMZN"],
                         value=asset,
                         placeholder='Наименование актива',
                         style={"marginTop": "20px", "width": "317px"}))


@app.callback(Output("table_update", "children"), [Input("price_field", "value"), Input("strike_field", "value"), Input("sigma_field", "value"), Input("risk_free_field", "value"), Input("start_date_field", 'start_date'), Input("start_date_field", 'end_date')])
def table(price, strike, sigma,risk_free, start_date, end_date):
    check_val = price, strike, sigma, risk_free, start_date, end_date
    if all(inp is not None for inp in check_val):
        calculator = Option(price, strike, sigma, datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                            datetime.datetime.strptime(end_date, '%Y-%m-%d').strftime('%d/%m/%Y'), risk_free)
        df = calculator.full_calc()
        return dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], id='greeks', style_header={'backgroundColor': 'grey','fontWeight': 'bold', 'textAlign':'center'}, style_cell_conditional=[{'if': {'column_id' : ' '}, 'minWidth': '135px', 'width': '135px', 'maxWidth': '135px',}, {'if': {'column_id' : 'Колл'}, 'width': '80px'}, {'if': {'column_id' : 'Пут'}, 'width': '80px'}])
    else:
        return dash_table.DataTable(blank.to_dict('records'), [{"name": i, "id": i} for i in blank.columns], id='greeks',
                                    style_cell_conditional=[
                                        {'if': {'column_id': ' '}, 'minWidth': '135px', 'width': '135px',
                                         'maxWidth': '135px'}, 
                                        {'if': {'column_id': 'Колл'}, 'width': '80px'},
                                        {'if': {'column_id': 'Пут'}, 'width': '80px'}],
                                        style_header={'backgroundColor': 'grey','fontWeight': 'bold', 'textAlign':'center'})



if __name__ == '__main__':
    app.run(debug=True)