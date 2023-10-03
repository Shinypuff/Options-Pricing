import dash
from dash import Input, Output, dash_table, no_update
from dash import dcc
from dash import html
from back import Option
from back import get_board
from Asian import MonteCarlo
from Asian import Hull
from dateutil import relativedelta
import pandas as pd
import datetime
import dash_bootstrap_components as dbc
from math import floor

data = [['Стоимость опциона', '', ''], ['Дельта', '', ''], ['Гамма', '', ''], ['Вега', '', ''], ['Тета', '', ''], ['Ро', '', '']]
data_asian = [["Колл", '', ''], ["Пут", '', '']]
blank = pd.DataFrame(data, columns=[' ', "Колл", "Пут"])
blank_asian = pd.DataFrame(data_asian, columns=[' ', "Халл", "Монте-Карло"])
empty_tree = pd.DataFrame(index=range(5), columns= [" "] * 6)
frame_on_load = []
on_type_check = ""
on_asset_check = ""

url = 'https://iss.moex.com/iss/statistics/engines/futures/markets/options/assets.html?limit=100&asset_type=S'
tickers_table = pd.read_html(url)[0]
tickers_list = tickers_table['asset (string:36)']

### styles ###
table_style = {"borderRadius": "10px", "overflow": "hidden", "border":"2px black solid", 'width':'500px'}
datatable_style = [{'if':{'column_id': 'Тикер'}, 'fontWeight': 'bold'}, {'background-color':'black', 'color':'white', 'textAlign':'center'}]
tree_style = [{'backgroundColor': 'black','fontWeight': 'bold', 'textAlign':'center', 'color':'white', 'border':'none', 'border-color':'black'},
              {'minWidth': '28px', 'width': '28px', 'maxWidth':'28px'},
              {"borderRadius": "10px", "overflow": "hidden", "border":"2px black solid", 'width':'250px'},
              [{"if": {"state": "selected"},
                                    "backgroundColor": "#dbdbdb",
                                    "border": "#454343 !important",},
                                    {'if': {'filter_query': '{0}>0', 'column_id':'0'}, 'backgroundColor' : 'lightblue'}]]
columns_to_color = ['Тикер', 'Теор. Цена', 'Посл. Цена', 'Bid', 'Offer']

row_style = {'margin':"10px 0px 0px 10px", 'width':'370'}
input_style = {"width": "100px", 'marginLeft':'50px'}

### App ###
app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])

### Components ###

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



asset_list = html.Div(
    dcc.Dropdown(id='asset_list', 
    options=tickers_list,
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
    dbc.Col(html.H6('Безрисковая ставка, %')),
    dbc.Col(dcc.Input(id='risk_free_field', value=10, type='number', style=input_style))
    ], style = row_style)

asian_1_field = dbc.Row([
    dbc.Col(html.H6('Кол-во точек усреднения')),
    dbc.Col(dcc.Input(id='avg_periods', value=2, type='number', style=input_style))
    ], style = row_style)

asian_2_field = dbc.Row([
    dbc.Col(html.H6('Дивидендная доходность, %')),
    dbc.Col(dcc.Input(id='div_yield', value=0, type='number', style=input_style))
    ], style = row_style)

asian_3_field = dbc.Row([
    dbc.Col(html.H6('Номер первой точки усреднения')),
    dbc.Col(dcc.Input(id='first_point', value=1, type='number', style=input_style))
    ], style = row_style)

asian_inputs = html.Div(children=[asian_1_field, asian_2_field, asian_3_field], style={'width':'450px',
                               "border":"2px black solid",
                               "marginTop":"10px",
                               "border-radius":"10px"})

asian_fin = html.Div(id="asian_input_div",
                               children = [html.Div(children=[html.H2("Границы периода"), asian_inputs]), html.Div(blank_table_asian, id='hull_carlo')])



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
                        'text-align':"center"})
            )

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

greeks_trees = dbc.Stack([greeks_table, trees], direction="horizontal", gap=3)

figure = html.Div( #html.Div(dcc.Graph(style = {"marginLeft":"10px"}), id='graph'),
                  id="graph_table",
                  style = {'width':'450px',
                            'height':'320', 
                            "marginTop":"10px",
                            "border-radius":"10px"},
                )

button = html.Div([html.Button(html.H4("Скачать данные", style={'fontWeight': 'bold'}), id="button_xlsx", style={"borderRadius": "10px", "overflow": "hidden", "border":"2px black solid", "width":"450px", "backgroundColor": "lightblue"}),
                  dcc.Download(id="download_xlsx")], style={"marginTop" : "20px"})


### Layout ###

default_layout = html.Div(id="page",
                      children=[
                        dbc.Row([
                            html.Div(style = {'width':'470px', "margin":"20px 0px 0px 100px"},
                                    children = [
                                        html.Div(html.H2(id='text', children = "Входные данные", style = {'text-align':'center', "marginBottom":"20px"})),
                                        
                                        html.Div(style={'width':'450px',
                                                        'height':'400px', 
                                                        "border":"2px black solid", 
                                                        "marginTop":"10px",
                                                        "border-radius":"10px"},
                                                 id="input_div",
                                                children =[asset_list, type_choice, price_field, strike_field, sigma_field, risk_free_field, date_field, figure, button])]),
                                
                            html.Div(id="calculator_div",
                                    style = {'width':'370px', 
                                    "marginLeft":"10px", 
                                    "marginTop":"32px"},
                                    children=[asian_fin, greeks_trees, board]),
                            ])
                      ], style={'height':'100%', 'width':'100%', 'max-width': '100%'})

app.layout = default_layout
@app.callback(Output("asian_input_div", "style"), Output("avg_periods", "value"), Input("type_choice", "value"), Input("date_field", 'end_date'))
def on_asian(type_choice, date):
    if type_choice=="Азиатский":
        return {}, floor((pd.to_datetime(date, dayfirst=True)-pd.to_datetime(datetime.date.today().strftime("%Y-%m-%d"), dayfirst=True)).days*252/365)
    return {'display':'none'}, floor((pd.to_datetime(date, dayfirst=True)-pd.to_datetime(datetime.date.today().strftime("%Y-%m-%d"), dayfirst=True)).days*252/365)

@app.callback([[Output("price_field", "value"), Output("strike_field", "value"), Output("sigma_field", "value"), Output("date_field", "end_date")],
               Output("graph_table", "children"), Output("call_board", "children"), Output("put_board", "children"), Output("stack_table", "style")],
              Input("asset_list", "value"), Input("type_choice", "value"))
def get_attributes(asset, type_choice):
    if asset==None:
        return [no_update, no_update, no_update, no_update], figure, html.Div(), html.Div(), {}
    call, put, params, fig, index = get_board(asset)
    fig.update_layout(margin=dict(l=10, r=0, t=20, b=10))

    pic = html.Div(dcc.Graph(figure=fig, style = {"marginLeft":"10px"}), 
                   style = {"border":"2px black solid", 
                            "borderRadius":"10px",
                            'width':'450px'
                            })
    call_board = dash_table.DataTable(call.to_dict('records'), [{"name": i, "id": i} for i in call.columns], style_data_conditional=[datatable_style[0],{'if':{'row_index': index}, 'backgroundColor': 'lightblue'},
                                                                                                                        {"if": {
                                                                                                                        "state": "selected"},
                                                                                                                        "backgroundColor": "#dbdbdb",
                                                                                                                        "border": "#757575 !important"}],
                                                                 style_header=datatable_style[1], style_data={'minWidth':'105px'})
    put_board = dash_table.DataTable(put.to_dict('records'), [{"name": i, "id": i} for i in put.columns], style_data_conditional=[datatable_style[0], {'if':{'row_index': index}, 'backgroundColor': 'lightblue'},
                                                                                                                        {"if": {
                                                                                                                        "state": "selected"},
                                                                                                                        "backgroundColor": "#dbdbdb",
                                                                                                                   "border": "#757575 !important"}], style_header=datatable_style[1], style_data={'minWidth':'105px'})
    clear_style = {'marginTop': '10px', "border": "2px black solid", "border": "2px black solid", 'width': '1300px'}
    if (type_choice=="Азиатский"):
        call_board, put_board, pic, clear_style = None, None, None, None
    if (globals()["on_type_check"]!=type_choice and globals()["on_asset_check"]==asset):
        globals()["on_type_check"] = type_choice
        globals()["on_asset_check"] = asset
        return [no_update, no_update, no_update, no_update], pic, call_board, put_board, clear_style
    globals()["on_type_check"] = type_choice
    globals()["on_asset_check"] = asset
    return params, pic, call_board, put_board, clear_style

@app.callback([Output("table_update", "children"), Output("stack_tree", "children"), Output("hull_carlo", "children")],
              [Input("price_field", "value"), Input("strike_field", "value"),
               Input("sigma_field", "value"), Input("risk_free_field", "value"),
               Input("date_field", 'start_date'), Input("date_field", 'end_date'),
               Input("type_choice", "value"), Input("avg_periods", "value"),
               Input("div_yield", "value"), Input("first_point", "value")])
def table(price, strike, sigma,risk_free, start_date, end_date, type_choice, avg_periods, div_yield, first_point):
    def debug_one_day(frame):
        if frame.shape[0]<=3:
            frame.loc[-1] = ["", ""]
            frame.sort_index(inplace=True)
            frame.loc[4] = ["", ""]
            frame["2"] = [0, "", 0, "", 0]
            frame.sort_index(inplace=True)
            return frame.reset_index(drop=True)
        else:
            return frame.iloc[calculator.days-2:calculator.days+3,:3]
    check_val_as = price, strike, sigma, risk_free, start_date, end_date, avg_periods, div_yield, first_point
    if (type_choice=="Азиатский"):
        if not all(inp is not None for inp in check_val_as):
            raise dash.exceptions.PreventUpdate()
        as_calculator = MonteCarlo(price, strike,risk_free, sigma, datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                            datetime.datetime.strptime(end_date, '%Y-%m-%d').strftime('%d/%m/%Y'), avg_periods, div_yield, first_point)
        as_calculator.sims()
        as_calculator.price()
        hull_price = Hull(price, strike,risk_free, sigma, datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                            datetime.datetime.strptime(end_date, '%Y-%m-%d').strftime('%d/%m/%Y'), div_yield) if first_point==1 else [" ", " "]

        out_asian = [["Колл", f'{hull_price[0]}', f'{as_calculator.call_price}'], ["Пут", f'{hull_price[1]}', f'{as_calculator.put_price}']]
        out_asian_table = pd.DataFrame(out_asian, columns=[' ', "Холл", "Монте-Карло"])
        datatable_asian = dash_table.DataTable(out_asian_table.to_dict('records'), [{"name": i, "id": i} for i in out_asian_table.columns],
                                       id='asians', style_header={'backgroundColor': 'black','fontWeight': 'bold', 'textAlign':'center', 'color':'white', 'border':'none', 'border-color':'black'},
                                       style_cell_conditional=[{'if': {'column_id' : ' '},'minWidth':'40px', 'width': '40px','maxWidth': '40px'},
                                                               {'if': {'column_id' : 'Холл'}, 'minWidth':'100px', 'width': '100px','maxWidth': '100px'},
                                                               {'if': {'column_id' : 'Монте-Карло'}, 'minWidth':'100px', 'width': '100px','maxWidth': '100px'}],
                                        style_table={"borderRadius": "10px", "overflow": "hidden", "border":"2px black solid", 'width':'450px', 'marginTop':'20px'},
                                        style_data_conditional=[{"if": {
                                                                "state": "selected"},
                                                                "backgroundColor": "#dbdbdb",
                                                                "border": "#454343 !important"}])

        return [None, None, datatable_asian]

    style = 0 if (type_choice=="Американский") else 1
    check_val = price, strike, sigma, risk_free, start_date, end_date

    if not all(inp is not None for inp in check_val):
        raise dash.exceptions.PreventUpdate()

    calculator = Option(price, strike, sigma, datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                        datetime.datetime.strptime(end_date, '%Y-%m-%d').strftime('%d/%m/%Y'), risk_free, style)


    greeks = calculator.full_calc() if (type_choice=="Европейский") else blank
    df = dash_table.DataTable(greeks.to_dict('records'), [{"name": i, "id": i} for i in greeks.columns],
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

    tree_opt_call = calculator.grow_tree(True)
    tree_opt_call_short = debug_one_day(tree_opt_call)
    tree_opt_put = calculator.grow_tree(False)
    tree_opt_put_short = debug_one_day(tree_opt_put)
    tree_asset = calculator.pretty_tree
    tree_asset_short = debug_one_day(tree_asset)

    globals()["frame_on_load"] = []
    globals()["frame_on_load"].extend([greeks, tree_asset, tree_opt_call, tree_opt_put])

    output = [[html.H2("Модель Блэка-Шоулза", style={'textAlign':'center'}), df],
                [dbc.Col([html.H3("Цена актива"), dash_table.DataTable(tree_asset_short.to_dict('records'), [{"name": i, "id": i} for i in tree_asset_short.columns], style_header=tree_style[0],
                                    style_data=tree_style[1],
                                    style_table=tree_style[2],
                                    style_data_conditional=tree_style[3])], style = {'textAlign':'center'}),
                dbc.Col([html.H3("Цена колл"), dash_table.DataTable(tree_opt_call_short.to_dict('records'), [{"name": i, "id": i} for i in tree_opt_call_short.columns], style_header=tree_style[0],
                                    style_data=tree_style[1],
                                    style_table=tree_style[2],
                                    style_data_conditional=tree_style[3])], style = {'textAlign':'center'}),
                dbc.Col([html.H3("Цена пут"), dash_table.DataTable(tree_opt_put_short.to_dict('records'), [{"name": i, "id": i} for i in tree_opt_put_short.columns], style_header=tree_style[0],
                                    style_data=tree_style[1],
                                    style_table=tree_style[2],
                                    style_data_conditional=tree_style[3])], style = {'textAlign':'center'})], dash_table.DataTable()]

        
    return output

@app.callback(Output("download_xlsx", "data"),
              Input("button_xlsx", "n_clicks"),
              prevent_initial_call=True,)
def on_download(n_clicks):
    with pd.ExcelWriter("Данные по опциону.xlsx") as writer:
        globals()["frame_on_load"][0].to_excel(writer, sheet_name="Модель Блэка-Шоулза", index=False)
        globals()["frame_on_load"][1].to_excel(writer, sheet_name="Дерево актива", index=False)
        globals()["frame_on_load"][2].to_excel(writer, sheet_name="Дерево колл", index=False)
        globals()["frame_on_load"][3].to_excel(writer, sheet_name="Дерево пут", index=False)

    return dcc.send_file("Данные по опциону.xlsx")

if __name__ == '__main__':
    app.run(debug=True)

