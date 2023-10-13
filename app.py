import dash.exceptions
from back import Option, get_board
from Asian import MonteCarlo, Hull
from math import floor
from layout import *


@app.callback(Output("averaging_field", "end_date"), Output("averaging_field", "start_date"), Input("date_field", "end_date"), Input("date_field", "start_date"))
def handle_averaging_period(initial_date_end, initial_date_start):
    return initial_date_end, initial_date_start

@app.callback(Output("asset_list", "options"), Output("risk_free_field", "value"), Input("asset_type", "value"))
def handle_asset_type(asset_type):
    if asset_type=="Акция":
        return tickers_list, 10
    elif asset_type=="Фьючерс":
        return futures_filter["asset"].unique(), 0
    return {"CNYRUB_TOM":"CNY/RUB", "EUR_RUB__TOM":"EUR/RUB", "USD000UTSTOM":"USD/RUB"}, 10


@app.callback(Output("futures_list", "options"), Input("asset_list", "value"))
def handle_futures_options(asset):
    return futures_filter[futures_filter["asset"]==f"{asset}"]["secid"].to_list()


@app.callback(Output("asset_list", "style"), Output("asset_list", "value"), Input("asset_type", "value"))
def handle_asset_list(asset_type):
    if asset_type != None:
        return visible_dropdowns, None
    return hidden_dropdowns, None


@app.callback(Output("futures_list", "style"), Output("futures_list", "value"), Input("asset_list", "value"),
              Input("asset_type", "value"))
def handle_futures_list(asset_list, asset_type):
    if asset_list != None and asset_type == "Фьючерс":
        return visible_dropdowns, no_update
    return hidden_dropdowns, None

# Choosing Asian Option results in other types changing their display to none
@app.callback(Output("asian_input_div", "style"), Output("greeks_trees", "style"), Input("type_choice", "value"))
def on_asian(type_choice):
    if type_choice=="Азиатский":
        return {}, {"display":"none"}
    return {'display':'none'}, {}

# avg_periods need to be calculated independently of type_choice. It helps to prevent recalculation of Asian option
# when choosing it

@app.callback(Output("avg_periods", "value"), Input("date_field", 'end_date'))
def maintain_periods(end_date):
    return floor((pd.to_datetime(end_date, dayfirst=True)-pd.to_datetime(datetime.date.today().strftime("%Y-%m-%d"),
                                                                         dayfirst=True)).days*252/365)


@app.callback([[Output("price_field", "value"), Output("strike_field", "value"), Output("sigma_field", "value"),
                Output("date_field", "end_date")], Output("graph_table", "children"), Output("call_board", "children"),
                Output("put_board", "children"), Output("stack_table", "style")],
                Input("asset_list", "value"), Input("type_choice", "value"), Input("futures_list", "value"),
                Input("asset_type", "value"))
def get_attributes(asset, type_choice, futures, asset_type):
    # Handling wrong secids of moex
    # Preventing update of inputs when the asset removed from dropdown
    if asset==None:
        return [no_update, no_update, no_update, no_update], figure, html.Div(), html.Div(), {}
    if futures == None and asset_type == "Фьючерс":
        raise dash.exceptions.PreventUpdate
    print(asset, futures)
    call, put, params, fig, index = get_board(asset) if futures == None and asset_type != "Фьючерс" else get_board(futures)
    fig.update_layout(margin=dict(l=10, r=0, t=20, b=10))

    pic = html.Div(dcc.Graph(figure=fig, style = {"marginLeft": "10px"}),
                   style={"border": "2px black solid",
                          "borderRadius": "10px",
                          'width': '450px'})

    call_board = dash_table.DataTable(call.to_dict('records'), [{"name": i, "id": i} for i in call.columns],
                                      style_data_conditional=[datatable_style[0],
                                      {'if': {'row_index': index}, 'backgroundColor': 'lightblue'},
                                      {"if": {"state": "selected"}, "backgroundColor": "#dbdbdb", "border": "#757575 !important"}],
                                      style_header=datatable_style[1], style_data={'minWidth': '105px'})

    put_board = dash_table.DataTable(put.to_dict('records'), [{"name": i, "id": i} for i in put.columns],
                                     style_data_conditional=[datatable_style[0], {'if':{'row_index': index}, 'backgroundColor': 'lightblue'},
                                     {"if": {"state": "selected"}, "backgroundColor": "#dbdbdb",
                                      "border": "#757575 !important"}], style_header=datatable_style[1], style_data={'minWidth':'105px'})

    clear_style = {'marginTop': '10px', "border": "2px black solid", "border": "2px black solid", 'width': '1300px'}
    # Hiding boards and pic when type is Asian
    if type_choice == "Азиатский":
        call_board, put_board, pic, clear_style = None, None, None, None

    # Preventing update of inputs when other type of option was chosen with the same asset
    if globals()["on_type_check"] != type_choice and globals()["on_asset_check"] == asset:
        globals()["on_type_check"] = type_choice
        globals()["on_asset_check"] = asset
        return [no_update, no_update, no_update, no_update], pic, call_board, put_board, clear_style
    globals()["on_type_check"] = type_choice
    globals()["on_asset_check"] = asset
    return params, pic, call_board, put_board, clear_style


@app.callback(Output("hull_carlo", "children"),
              [Input("price_field", "value"), Input("strike_field", "value"),
               Input("sigma_field", "value"), Input("risk_free_field", "value"),
               Input("date_field", 'start_date'), Input("date_field", 'end_date'),
               Input("avg_periods", "value"), Input("div_yield", "value"), Input("averaging_field", "start_date"),
               Input("averaging_field", "end_date")])
def hull_carlo(price, strike, sigma, risk_free, start_date, end_date, avg_periods, div_yield, avg_start, avg_end):
    check_val_as = price, strike, sigma, risk_free, start_date, end_date, avg_periods, div_yield, avg_start, avg_end
    if not all(inp is not None for inp in check_val_as):
        raise dash.exceptions.PreventUpdate()
    as_calculator = MonteCarlo(price, strike, risk_free, sigma,
                               datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                               datetime.datetime.strptime(end_date, '%Y-%m-%d').strftime('%d/%m/%Y'), avg_periods,
                               div_yield,
                               datetime.datetime.strptime(avg_start, '%Y-%m-%d').strftime('%d/%m/%Y'),
                               datetime.datetime.strptime(avg_end, '%Y-%m-%d').strftime('%d/%m/%Y'))
    as_calculator.sims()
    as_calculator.price()
    hull_price = Hull(price, strike, risk_free, sigma,
                      datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                      datetime.datetime.strptime(end_date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                      div_yield) if start_date==avg_start and end_date==avg_end else [" ", " "]

    out_asian = [["Колл", f'{hull_price[0]}', f'{as_calculator.call_price}'],
                 ["Пут", f'{hull_price[1]}', f'{as_calculator.put_price}']]
    out_asian_table = pd.DataFrame(out_asian, columns=[' ', "Холл", "Монте-Карло"])
    datatable_asian = dash_table.DataTable(out_asian_table.to_dict('records'),
                                           [{"name": i, "id": i} for i in out_asian_table.columns],
                                           id='asians', style_header=asian_datatable_style[0],
                                           style_cell_conditional=asian_datatable_style[1],
                                           style_table=asian_datatable_style[2],
                                           style_data_conditional=asian_datatable_style[3])

    return datatable_asian


@app.callback([Output("table_update", "children"), Output("stack_tree", "children")],
              [Input("price_field", "value"), Input("strike_field", "value"),
               Input("sigma_field", "value"), Input("risk_free_field", "value"),
               Input("date_field", 'start_date'), Input("date_field", 'end_date'),
               Input("type_choice", "value")])
def table(price, strike, sigma, risk_free, start_date, end_date, type_choice):

    # Debug 1-day gap
    def debug_one_day(frame):
        if frame.shape[0] <= 3:
            frame.loc[-1] = ["", ""]
            frame.sort_index(inplace=True)
            frame.loc[4] = ["", ""]
            frame["2"] = [0, "", 0, "", 0]
            frame.sort_index(inplace=True)
            return frame.reset_index(drop=True)
        else:
            return frame.iloc[calculator.days-2:calculator.days+3, :3]

    style = 0 if (type_choice == "Американский") else 1
    check_val = price, strike, sigma, risk_free, start_date, end_date

    if not all(inp is not None for inp in check_val):
        raise dash.exceptions.PreventUpdate()

    calculator = Option(price, strike, sigma, datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%d/%m/%Y'),
                        datetime.datetime.strptime(end_date, '%Y-%m-%d').strftime('%d/%m/%Y'), risk_free, style)

    greeks = calculator.full_calc() if (type_choice == "Европейский") else blank
    df = dash_table.DataTable(greeks.to_dict('records'), [{"name": i, "id": i} for i in greeks.columns],
                              id='greeks', style_header={'backgroundColor': 'black', 'fontWeight': 'bold',
                                                         'textAlign': 'center', 'color': 'white', 'border': 'none',
                                                         'border-color': 'black'},
                              style_cell_conditional=[{'if': {'column_id': ' '}, 'minWidth': '80px', 'width': '80px',
                                                       'maxWidth': '80px'}, {'if': {'column_id': 'Колл'},
                                                       'minWidth': '60px', 'width': '60px', 'maxWidth': '60px'},
                                                       {'if': {'column_id' : 'Пут'}, 'minWidth': '60px',
                                                        'width': '60px', 'maxWidth': '60px'}],
                              style_table=table_style,
                              style_data_conditional=[{'if': {'row_index': 0}, 'backgroundColor': 'lightblue'},
                                                      {"if": {"state": "selected"},
                                                       "backgroundColor": "#dbdbdb",
                                                       "border": "#454343 !important"}])

    tree_opt_call = calculator.grow_tree(True)
    tree_opt_call_short = debug_one_day(tree_opt_call)
    tree_opt_put = calculator.grow_tree(False)
    tree_opt_put_short = debug_one_day(tree_opt_put)
    tree_asset = calculator.pretty_tree
    tree_asset_short = debug_one_day(tree_asset)

    # List for saving to excel
    globals()["frame_on_load"] = []
    globals()["frame_on_load"].extend([greeks, tree_asset, tree_opt_call, tree_opt_put])

    output = [[html.H2("Модель Блэка-Шоулза", style={'textAlign': 'center'}), df],
              [dbc.Col([html.H3("Цена актива"), dash_table.DataTable(tree_asset_short.to_dict('records'),
                                    [{"name": i, "id": i} for i in tree_asset_short.columns], style_header=tree_style[0],
                                    style_data=tree_style[1],
                                    style_table=tree_style[2],
                                    style_data_conditional=tree_style[3])], style = {'textAlign':'center'}),
              dbc.Col([html.H3("Цена колл"), dash_table.DataTable(tree_opt_call_short.to_dict('records'),
                                    [{"name": i, "id": i} for i in tree_opt_call_short.columns], style_header=tree_style[0],
                                    style_data=tree_style[1],
                                    style_table=tree_style[2],
                                    style_data_conditional=tree_style[3])], style = {'textAlign':'center'}),
              dbc.Col([html.H3("Цена пут"), dash_table.DataTable(tree_opt_put_short.to_dict('records'),
                                    [{"name": i, "id": i} for i in tree_opt_put_short.columns], style_header=tree_style[0],
                                    style_data=tree_style[1],
                                    style_table=tree_style[2],
                                    style_data_conditional=tree_style[3])], style = {'textAlign':'center'})]]

    return output


@app.callback(Output("download_xlsx", "data"),
              Input("button_xlsx", "n_clicks"), Input("asset_list", "value"),
              prevent_initial_call=True,)
def on_download(n_clicks, asset):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "button_xlsx" in changed_id:
        data_name = "опциону" if asset == None else asset
        print(data_name)
        with pd.ExcelWriter(f"Данные по {data_name}.xlsx") as writer:
            globals()["frame_on_load"][0].to_excel(writer, sheet_name="Модель Блэка-Шоулза", index=False)
            globals()["frame_on_load"][1].to_excel(writer, sheet_name="Дерево актива", index=False)
            globals()["frame_on_load"][2].to_excel(writer, sheet_name="Дерево колл", index=False)
            globals()["frame_on_load"][3].to_excel(writer, sheet_name="Дерево пут", index=False)

        return dcc.send_file(f"Данные по {data_name}.xlsx")


if __name__ == '__main__':
    app.run(debug=True)
