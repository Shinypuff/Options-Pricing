from dash import Input, Output, dash_table, no_update
from dash import dcc
from dash import html
from dateutil import relativedelta
import datetime
import dash_bootstrap_components as dbc
from table_create import *
from styles import *

blank_table_asian = html.Div(children=dash_table.DataTable(blank_asian.to_dict('records'), [{"name": i, "id": i} for i in blank_asian.columns],
                                       style_header={'backgroundColor': 'black','fontWeight': 'bold', 'textAlign':'center', 'color':'white', 'border':'none', 'border-color':'black'},
                                       style_cell_conditional=[{'if': {'column_id' : ' '},'minWidth':'40px', 'width': '40px','maxWidth': '40px'},
                                                               {'if': {'column_id' : 'Халл'}, 'minWidth':'100px', 'width': '100px','maxWidth': '100px'},
                                                               {'if': {'column_id' : 'Монте-Карло'}, 'minWidth':'100px', 'width': '100px','maxWidth': '100px'}],
                                        style_table={"borderRadius": "10px", "overflow": "hidden", "border":"2px black solid", 'width':'450px', 'marginTop':'20px'},
                                        style_data_conditional=[{"if": {
                                                                "state": "selected"},
                                                                "backgroundColor": "#dbdbdb",
                                                                "border": "#454343 !important"}]), id='asians')

blank_table = dash_table.DataTable(blank.to_dict('records'), [{"name": i, "id": i} for i in blank.columns],
                                       id='greeks', style_header={'backgroundColor': 'black','fontWeight': 'bold', 'textAlign':'center', 'color':'white', 'border':'none', 'border-color':'black'},
                                       style_cell_conditional=[{'if': {'column_id' : ' '}, 'minWidth': '80px', 'width': '80px', 'maxWidth': '80px',},
                                                               {'if': {'column_id' : 'Колл'}, 'minWidth': '60px', 'width': '60px', 'maxWidth': '60px'},
                                                               {'if': {'column_id' : 'Пут'}, 'minWidth': '60px', 'width': '60px', 'maxWidth': '60px'}],
                                        style_table=table_style,
                                        style_data_conditional=[{'if':{'row_index': 0}, 'backgroundColor': 'lightblue'},
                                                                {"if": {
                                                                "state": "selected"},
                                                                "backgroundColor": "#dbdbdb",
                                                                "border": "#454343 !important"}])



asset_type = html.Div(
    dcc.Dropdown(id='asset_type',
    options=["Акция", "Фьючерс", "Валюта"],
    placeholder='Тип базового актива',
    style = {'marginRight':"25px",
             'marginLeft':"8px",
             'marginTop':"30px",
             'marginBottom':"10px",
             "width" : "370px"})
)

asset_list = html.Div(
    dcc.Dropdown(id='asset_list',
    options=tickers_list,
    placeholder='Базовый актив',
    style = {'marginRight':"25px",
             'marginLeft':"8px",
             "width" : "370px",
             'display': 'none',
             'marginBottom':'10px',
             'marginTop':'-5px'}))

futures_list = html.Div(
    dcc.Dropdown(id='futures_list',
    options=futures_filter["secid"].to_list(),
    placeholder='Фьючерс',
    style = {'marginRight':"25px",
             'marginLeft':"8px",
             "width" : "370px",
             'display': 'none',
             'marginBottom':'10px',
             'marginTop':'-5px'}))

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
    dbc.Col(html.H6('Безрисковая ставка, %')),
    dbc.Col(dcc.Input(id='risk_free_field', value=10, type='number', style=input_style))
    ], style = row_style)

asian_1_field = dbc.Row([
    dbc.Col(html.H6('Кол-во точек до экспирации')),
    dbc.Col(dcc.Input(id='avg_periods', value=2, type='number', style=input_style))
    ], style = row_style)

asian_2_field = dbc.Row([
    dbc.Col(html.H6('Дивидендная доходность, %')),
    dbc.Col(dcc.Input(id='div_yield', value=0, type='number', style=input_style))
    ], style = row_style)


date_field = html.Div(
        dcc.DatePickerRange(
                id='date_field',
                clearable=True,
                display_format='D.M.Y',
                start_date=datetime.date.today().strftime("%Y-%m-%d"),
                end_date=(datetime.date.today() + relativedelta.relativedelta(months=1)).strftime("%Y-%m-%d"),
                style= {"width": "400px",
                        'marginRight':"25px",
                        'marginLeft':"20px",
                        'marginBottom':"20px",
                        'marginTop':"20px",
                        'text-align':"center"}))

averaging_field = html.Div(
        dcc.DatePickerRange(
                id='averaging_field',
                clearable=True,
                display_format='D.M.Y',
                start_date=datetime.date.today().strftime("%Y-%m-%d"),
                end_date=(datetime.date.today() + relativedelta.relativedelta(months=1)).strftime("%Y-%m-%d"),
                style= {"width": "400px",
                        'marginRight':"25px",
                        'marginLeft':"20px",
                        'marginBottom':"20px",
                        'marginTop':"20px",
                        'text-align':"center"}))

asian_inputs = html.Div(children=[asian_1_field, asian_2_field, averaging_field], style={'width':'450px',
                               "border":"2px black solid",
                               "marginTop":"10px",
                               "border-radius":"10px"})



asian_fin = html.Div(id="asian_input_div",
                               children = [html.Div(children=[html.H2("Границы периода"), asian_inputs]), html.Div(blank_table_asian, id='hull_carlo')])


greeks_table = html.Div(id='table_update',
                        children=[html.H2("Модель Блэка-Шоулза", style={'textAlign':'center'}), blank_table])

board = dbc.Stack([
    dbc.Col(dash_table.DataTable(), id='call_board'),
    dbc.Col(dash_table.DataTable(), id='put_board')
    ], id='stack_table', direction='horizontal', style ={})

trees = dbc.Stack([
    dbc.Col([dash_table.DataTable()],),
    dbc.Col([dash_table.DataTable()], id='call_tree'),
    dbc.Col([dash_table.DataTable()], id='put_tree')
    ], id='stack_tree', direction='horizontal', style ={"marginTop":"34px"}, gap=3)

greeks_trees = dbc.Stack([greeks_table, trees], direction="horizontal", gap=3, id="greeks_trees")

figure = html.Div( #html.Div(dcc.Graph(style = {"marginLeft":"10px"}), id='graph'),
                  id="graph_table",
                  style = {'width':'450px',
                            'height':'320',
                            "marginTop":"10px",
                            "border-radius":"10px"},
                )

button = html.Div([html.Button(html.H4("Скачать данные", style={'fontWeight': 'bold'}), id="button_xlsx", style={"borderRadius": "10px", "overflow": "hidden", "border":"2px black solid", "width":"450px", "backgroundColor": "lightblue"}),
                  dcc.Download(id="download_xlsx")], style={"marginTop" : "20px"})
