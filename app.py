import dash
from dash import Input, Output
from dash import dcc
from dash import html
from datetime import date

app = dash.Dash(__name__)

app.layout = html.Div(id="input_cells", children=(html.H1(id='text', children = "Ochko"),
                                html.Div(id='dropdowns', children=(dcc.Dropdown(id='asset_list', options=["ABMN", "AMZN"], placeholder='Наименование актива', style = {"marginTop" : "20px", "width" : "317px"}))),
                                html.Div([dcc.RadioItems(id='type_choice', options=['Европейский', 'Американский'], inline=True)], style = {"margin" : "10px 0px 0px 70px"}),
                                html.Div([dcc.Input(id='price_field', type='number', placeholder='Цена актива', style= {"width": "308px","marginTop" : "10px"})]),
                                html.Div([dcc.Input(id='strike_field', type='number', placeholder='Цена исполнения', style= {"width": "308px","marginTop" : "10px"})]),
                                html.Div([dcc.Input(id='sigma_field', type='number', placeholder='Волатильность, %', style= {"width": "308px","marginTop" : "10px"})]),
                                html.Div([dcc.Input(id='risk_free_field', type='number', placeholder='Безрисковая ставка, %', style= {"width": "308px","marginTop" : "10px"})]),
                                html.Div([dcc.DatePickerRange(id='start_date_field', clearable=True, display_format='D.M.Y',end_date=date(2024, 12, 12), style= {"width": "500px","marginTop" : "10px", "font-size": "2px"})]),
                                html.Div([dcc.Input(id='number_of_steps', type='text', placeholder='Количество шагов дерева', style= {"width": "200px","marginTop" : "10px"})])))


@app.callback(Output("dropdowns", "children"), Input("asset_list", "value"))
def get_attributes(asset):
    print(asset)
    if asset!=None:
        return (dcc.Dropdown(id='asset_list', options=["ABMN", "AMZN"],
                                                               value=asset, placeholder='Наименование актива',
                                                               style={"marginTop": "20px", "width": "317px"}),
                dcc.Dropdown(id='stock_future_list',
                             options=["Фьючерсы", "Акции", None], value='string',
                             placeholder='Тип базового актива',
                             style={"marginTop": "20px", "width": "317px"}))
    return (dcc.Dropdown(id='asset_list', options=["ABMN", "AMZN"],
                                                               value=asset, placeholder='Наименование актива',
                                                               style={"marginTop": "20px", "width": "317px"}))



if __name__ == '__main__':
    app.run(debug=True)