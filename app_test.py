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
empty_tree = pd.DataFrame(index=range(5), columns= [" "] * 6)

### styles ###
table_style = {"borderRadius": "10px", "overflow": "hidden", "border":"2px black solid", 'width':'500px'}
datatable_style = [{'if':{'column_id': 'Тикер'}, 'fontWeight': 'bold'}, {'background-color':'black', 'color':'white'}]
columns_to_color = ['Тикер', 'Теор. Цена', 'Посл. Цена', 'Bid', 'Offer']

row_style = {'margin':"10px 0px 0px 10px", 'width':'370'}
input_style = {"width": "100px", 'marginLeft':'50px'}

### App ###
app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])

### Components ###

asset_list = html.Div(
    dcc.Dropdown(id='asset_list', 
    options=["YNDX", "SBER", "RUAL"], 
    placeholder='Наименование актива', 
    style = {'marginRight':"25px", 
             'marginLeft':"8px", 
             'marginTop':"30px", 
             "width" : "370px"})
)

type_choice = html.Div([dcc.RadioItems(id='type_choice', 
                                       options=['Европейский', 'Американский', 'Азиатский'],
                                       value='Европейский',
                                       labelStyle = {'margin':'7px'},
                                       inputStyle = {'margin':'3px'}, 
                                       inline=False)], 
                                       style = {"marginLeft" : "10px", 'text-align':'left', 'width':'370px'})

price_field = dbc.Row([
    dbc.Col(html.H6('Цена актива')),
    dbc.Col(dcc.Input(id='price_field', value=100, type='number', style=input_style))
    ], style = row_style)

strike_field =  dbc.Row([
    dbc.Col(html.H6('Цена исполнения')),
    dbc.Col(dcc.Input(id='strike_field', value=100, type='number', style=input_style))
    ], style = row_style)

sigma_field = dbc.Row([
     dbc.Col(html.H6('Волатильность, %')),
     dbc.Col(dcc.Input(id='sigma_field', value=10, type='number', style=input_style))
     ], style = row_style)

risk_free_field = dbc.Row([
    dbc.Col(html.H6('Безрисоквая ставка, %')),
    dbc.Col(dcc.Input(id='risk_free_field', value=10, type='number', style=input_style))
    ], style = row_style)

date_field = html.Div(
        dcc.DatePickerRange(
                id='date_field', 
                clearable=True, 
                display_format='D.M.Y',
                start_date=datetime.datetime.now().strftime('%Y-%m-%d'), 
                end_date=datetime.datetime.now().strftime('2024-%m-%d'), 
                style= {"width": "400px",
                        'marginRight':"25px",
                        'marginLeft':"20px",
                        'marginBottom':"20px",
                        'marginTop':"20px",
                        'text-align':"center"})
            )    
                                            
greeks_table = html.Div(id='table_update', 
                        children=dash_table.DataTable(
                            blank.to_dict('records'), [{"name": i, "id": i} for i in blank.columns], 
                            id='greeks', 
                            style_header={'backgroundColor': 'grey','fontWeight': 'bold'},
                            style_as_list_view=False, style_table = table_style))

board = dbc.Stack([
    dbc.Col(dash_table.DataTable(), id='call_board'),
    dbc.Col(dash_table.DataTable(), id='put_board')
    ], id='stack_table', direction='horizontal', style ={})

figure = html.Div( #html.Div(dcc.Graph(style = {"marginLeft":"10px"}), id='graph'),
                  id="graph_table",
                  style = {'width':'450px',
                            'height':'320', 
                            "marginTop":"30px",
                            "border-radius":"10px"},
                )

### Layout ###

default_layout = html.Div(id="page",
                      children=[
                        dbc.Row([
                            html.Div(style = {'width':'470px', "margin":"20px 0px 0px 100px"},
                                    children = [
                                        html.Div(html.H1(id='text', children = "Входные данные", style = {'text-align':'center', "marginBottom":"20px"})),
                                        
                                        html.Div(style={'width':'450px',
                                                        'height':'400px', 
                                                        "border":"2px black solid", 
                                                        "marginTop":"10px",
                                                        "border-radius":"10px"}, 
                                                
                                                children =[asset_list, type_choice, price_field, strike_field, sigma_field, risk_free_field, date_field, figure])]),
                                
                            html.Div(id="calculator_div",
                                    style = {'width':'370px', 
                                    "marginLeft":"10px", 
                                    "marginTop":"87px"}, 
                                    children=[greeks_table, board]), 
                            ])
                      ])

app.layout = default_layout

@app.callback([[Output("price_field", "value"), Output("strike_field", "value"), Output("sigma_field", "value"), Output("date_field", "end_date")],
               Output("graph_table", "children"), Output("call_board", "children"), Output("put_board", "children"), Output("stack_table", "style")],
              Input("asset_list", "value"))
def get_attributes(asset):
    if asset==None:
        return [100, 100, 10, datetime.datetime.now().strftime('2024-%m-%d')], figure, html.Div(), html.Div(), {}
    call, put, params, fig, index = get_board(asset)

    fig.update_layout(margin=dict(l=10, r=0, t=20, b=10))

    pic = html.Div(dcc.Graph(figure=fig, style = {"marginLeft":"10px"}), 
                   style = {"border":"2px black solid", 
                            "borderRadius":"10px",
                            'width':'450px'
                            })

    return params, pic, dash_table.DataTable(call.to_dict('records'), [{"name": i, "id": i} for i in call.columns], style_data_conditional=[datatable_style[0],{'if':{'row_index': index}, 'backgroundColor': 'lightblue'}], style_header=datatable_style[1], style_data={'minWidth':'105px'}), \
           dash_table.DataTable(put.to_dict('records'), [{"name": i, "id": i} for i in put.columns], style_data_conditional=[datatable_style[0], {'if':{'row_index': index}, 'backgroundColor': 'lightblue'}], style_header=datatable_style[1], style_data={'minWidth':'105px'}),\
           {'marginTop': '10px', "border": "2px black solid", "border": "2px black solid", 'width': '1300px'}

@app.callback([Output("table_update", "children")],
              [Input("price_field", "value"), Input("strike_field", "value"),
               Input("sigma_field", "value"), Input("risk_free_field", "value"),
               Input("date_field", 'start_date'), Input("date_field", 'end_date'),
               Input("type_choice", "value")])
def table(price, strike, sigma,risk_free, start_date, end_date, type_choice):

    check_val = price, strike, sigma, risk_free, start_date, end_date
    if all(inp is not None for inp in check_val):
        calculator = Option(price, strike, sigma, datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                            datetime.datetime.strptime(end_date, '%Y-%m-%d').strftime('%d/%m/%Y'), risk_free)

        df = calculator.full_calc()
        output = [dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], 
                                       id='greeks', style_header={'backgroundColor': 'black','fontWeight': 'bold', 'textAlign':'center', 'color':'white', 'border':'none', 'border-color':'black'},
                                       style_cell_conditional=[{'if': {'column_id' : ' '}, 'minWidth': '80px', 'width': '80px', 'maxWidth': '80px',}, 
                                                               {'if': {'column_id' : 'Колл'}, 'width': '60px'}, 
                                                               {'if': {'column_id' : 'Пут'}, 'width': '60px'}], 
                                        style_table=table_style,
                                        style_data_conditional=[{'if':{'row_index': 0}, 'backgroundColor': 'lightblue'}])]
        
        if type_choice == 'Американский':
            output[0] = html.H1(children="Нельзя")
            return output
        
        return output

    else:
        return [dash_table.DataTable(blank.to_dict('records'), [{"name": i, "id": i} for i in blank.columns], id='greeks',
                                    style_cell_conditional=[
                                        {'if': {'column_id': ' '}, 'minWidth': '80px', 'width': '80px', 'maxWidth': '80px'}, 
                                        {'if': {'column_id': 'Колл'}, 'width': '60px'},
                                        {'if': {'column_id': 'Пут'}, 'width': '60px'}],
                                        style_header={'backgroundColor': 'black','fontWeight': 'bold', 'textAlign':'center', 'color':'white', 'border':'none', 'border-color':'black'}, style_table = table_style), dash_table.DataTable(empty_tree.to_dict('records'), [{"name": i, "id": i} for i in empty_tree.columns]), dash_table.DataTable(empty_tree.to_dict('records'), [{"name": i, "id": i} for i in empty_tree.columns]),
                                        dash_table.DataTable(empty_tree.to_dict('records'), [{"name": i, "id": i} for i in empty_tree.columns]),dash_table.DataTable(empty_tree.to_dict('records'), [{"name": i, "id": i} for i in empty_tree.columns])]


if __name__ == '__main__':
    app.run(debug=True)