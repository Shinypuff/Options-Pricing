import dash
from dash import Input, Output, dash_table
from dash import dcc
from dash import html
from datetime import date
from back import Option
from back import get_board
import numpy as np
import time
import pandas as pd
import datetime
import dash_bootstrap_components as dbc

data = [['Стоимость опциона', '', ''], ['Дельта', '', ''], ['Гамма', '', ''], ['Вега', '', ''], ['Тета', '', ''], ['Ро', '', '']]
blank = pd.DataFrame(data, columns=[' ', "Колл", "Пут"])
empty_tree = pd.DataFrame(index=range(10), columns= [" "] * 11)

app = dash.Dash(__name__)

app.layout = html.Div(id="page", children=(html.Div(id="input_cells", children=(html.H1(id='text', children = "Ввод"),
                                html.Div(id='dropdowns', children=(dcc.Dropdown(id='asset_list', options=["YNDX", "SBER", "RUAL"], placeholder='Наименование актива', style = {"marginTop" : "20px", "width" : "317px"}))),
                                html.Div([dcc.RadioItems(id='type_choice', options=['Европейский', 'Американский'], inline=True)], style = {"margin" : "10px 0px 0px 40px"}),
                                html.Div([dcc.Input(id='price_field', value=100, type='number', placeholder='Цена актива', style= {"width": "308px","marginTop" : "10px"})]),
                                html.Div([dcc.Input(id='strike_field', value=100, type='number', placeholder='Цена исполнения', style= {"width": "308px","marginTop" : "10px"})]),
                                html.Div([dcc.Input(id='sigma_field', value=10, type='number', placeholder='Волатильность, %', style= {"width": "308px","marginTop" : "10px"})]),
                                html.Div([dcc.Input(id='risk_free_field', value=10, type='number', placeholder='Безрисковая ставка, %', style= {"width": "308px","marginTop" : "10px"})]),
                                html.Div([dcc.DatePickerRange(id='start_date_field', clearable=True, display_format='D.M.Y',start_date=datetime.datetime.now().strftime('%Y-%m-%d'), end_date=datetime.datetime.now().strftime('2024-%m-%d'), style= {"width": "500px","marginTop" : "10px"})]),
                                html.Div([dcc.Input(id='number_of_steps', type='text', placeholder='Количество шагов дерева', style= {"width": "200px","marginTop" : "10px"})])), style={'display':'inline-block'}),
                      
                      html.Div(id="calculator_div", children=(html.Div(id='results', children=(html.Div(id='put_part', children=(html.H1(id='calculated', children='Результаты'), html.Div(id='table_update', children=dash_table.DataTable(blank.to_dict('records'), [{"name": i, "id": i} for i in blank.columns], id='greeks', style_header={'backgroundColor': 'red','fontWeight': 'bold'}, style_as_list_view=True))), style={'display':'inline-block'})), style={'display' : 'flex'})),
                               style={'display':'inline-block', 'width':'19%'}),
                      html.Div(id="tree_call", children=(html.Div(id="pretty_tree", children=(dash_table.DataTable())), html.Div(id="pretty_opt", children=(dash_table.DataTable()))),style={"display" : "inline-block"}),
                      html.Div(id="tree_put", children=(html.Div(id="pretty_tree_put", children=(dash_table.DataTable())), html.Div(id="pretty_opt_put", children=(dash_table.DataTable()))),style={"display" : "inline-block"}),
                      html.Div(children=[dbc.Row(id='graph', children=dcc.Graph()), dbc.Row(id='tables', children=[dash_table.DataTable(), dash_table.DataTable()])],id="graph_table", style = {'display' : 'inline-block'})), style={'display':'flex'})


@app.callback([[Output("price_field", "value"), Output("strike_field", "value"), Output("sigma_field", "value")],
               Output("graph", "children"), Output("tables", "children")],
              Input("asset_list", "value"))
def get_attributes(asset):

    call, put, params, fig = get_board(asset)
    print(call)
    return params, dcc.Graph(figure=fig), [dash_table.DataTable(call.to_dict('records'), [{"name": i, "id": i} for i in call.columns]),
                                           dash_table.DataTable(put.to_dict('records'), [{"name": i, "id": i} for i in put.columns])]

@app.callback([Output("table_update", "children"), Output("pretty_tree", "children"),
               Output("pretty_opt", "children"), Output("pretty_tree_put", "children"),
               Output("pretty_opt_put", "children")],
              [Input("price_field", "value"), Input("strike_field", "value"),
               Input("sigma_field", "value"), Input("risk_free_field", "value"),
               Input("start_date_field", 'start_date'), Input("start_date_field", 'end_date'),
               Input("type_choice", "value")])
def table(price, strike, sigma,risk_free, start_date, end_date, type_choice):

    check_val = price, strike, sigma, risk_free, start_date, end_date
    if all(inp is not None for inp in check_val):
        calculator = Option(price, strike, sigma, datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                            datetime.datetime.strptime(end_date, '%Y-%m-%d').strftime('%d/%m/%Y'), risk_free)

        trees_call = calculator.grow_tree(call = True)
        trees_call[0].drop(0, inplace=True)
        trees_call[1].drop(0, inplace=True)
        trees_call[0].columns = [str(i) for i in range(11)]
        trees_call[1].columns = [str(i) for i in range(11)]
        trees_put = calculator.grow_tree(call = False)
        trees_put[0].drop(0, inplace=True)
        trees_put[1].drop(0, inplace=True)
        trees_put[0].columns = [str(i) for i in range(11)]
        trees_put[1].columns = [str(i) for i in range(11)]

        df = calculator.full_calc()
        output = [dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], id='greeks', style_header={'backgroundColor': 'grey','fontWeight': 'bold', 'textAlign':'center'}, style_cell_conditional=[{'if': {'column_id' : ' '}, 'minWidth': '135px', 'width': '135px', 'maxWidth': '135px',}, {'if': {'column_id' : 'Колл'}, 'width': '80px'}, {'if': {'column_id' : 'Пут'}, 'width': '80px'}]),
        dash_table.DataTable(trees_call[0].to_dict('records'), [{"name": i, "id": i} for i in trees_call[0].columns], style_header = {'display': 'none'}), dash_table.DataTable(trees_call[1].to_dict('records'), [{"name": i, "id": i} for i in trees_call[1].columns], style_header = {'display': 'none'}),
        dash_table.DataTable(trees_put[0].to_dict('records'), [{"name": i, "id": i} for i in trees_put[0].columns], style_header = {'display': 'none'}), dash_table.DataTable(trees_put[1].to_dict('records'), [{"name": i, "id": i} for i in trees_put[1].columns], style_header = {'display': 'none'})]
        if type_choice == 'Американский':
            output[0] = html.H1(children="Сосу")
            return output
        return output

    else:
        return (dash_table.DataTable(blank.to_dict('records'), [{"name": i, "id": i} for i in blank.columns], id='greeks',
                                    style_cell_conditional=[
                                        {'if': {'column_id': ' '}, 'minWidth': '135px', 'width': '135px',
                                         'maxWidth': '135px'}, 
                                        {'if': {'column_id': 'Колл'}, 'width': '80px'},
                                        {'if': {'column_id': 'Пут'}, 'width': '80px'}],
                                        style_header={'backgroundColor': 'grey','fontWeight': 'bold', 'textAlign':'center'}), dash_table.DataTable(empty_tree.to_dict('records'), [{"name": i, "id": i} for i in empty_tree.columns]), dash_table.DataTable(empty_tree.to_dict('records'), [{"name": i, "id": i} for i in empty_tree.columns]),
                                        dash_table.DataTable(empty_tree.to_dict('records'), [{"name": i, "id": i} for i in empty_tree.columns]),dash_table.DataTable(empty_tree.to_dict('records'), [{"name": i, "id": i} for i in empty_tree.columns]))


if __name__ == '__main__':
    app.run(debug=True)