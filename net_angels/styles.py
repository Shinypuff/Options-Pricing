table_style = {"borderRadius": "10px", "overflow": "hidden", "border":"2px black solid", 'width':'500px'}
datatable_style = [{'if':{'column_id': 'Тикер'}, 'fontWeight': 'bold'}, {'background-color':'black', 'color':'white', 'textAlign':'center'}]
asian_datatable_style = [{'backgroundColor': 'black', 'fontWeight': 'bold', 'textAlign': 'center', 'color': 'white', 'border': 'none', 'border-color': 'black'},
                         [{'if': {'column_id': ' '}, 'minWidth': '40px', 'width': '40px','maxWidth': '40px'},{'if': {'column_id': 'Холл'}, 'minWidth': '100px', 'width': '100px','maxWidth': '100px'},
                                                 {'if': {'column_id': 'Монте-Карло'}, 'minWidth': '100px',
                                                 'width': '100px', 'maxWidth': '100px'}],
                         {"borderRadius": "10px", "overflow": "hidden", "border": "2px black solid", 'width': '450px', 'marginTop': '20px'},
                         [{"if": {"state": "selected"}, "backgroundColor": "#dbdbdb", "border": "#454343 !important"}]]
tree_style = [{'backgroundColor': 'black','fontWeight': 'bold', 'textAlign':'center', 'color':'white', 'border':'none', 'border-color':'black'},
              {'minWidth': '28px', 'width': '28px', 'maxWidth':'28px'},
              {"borderRadius": "10px", "overflow": "hidden", "border":"2px black solid", 'width':'250px'},
              [{"if": {"state": "selected"},
                                    "backgroundColor": "#dbdbdb",
                                    "border": "#454343 !important",},
                                    {'if': {'filter_query': '{0}>0', 'column_id': '0'}, 'backgroundColor': 'lightblue'}]]
columns_to_color = ['Тикер', 'Теор. Цена', 'Посл. Цена', 'Bid', 'Offer']

row_style = {'margin':"10px 0px 0px 10px", 'width': '370'}
input_style = {"width": "100px", 'marginLeft': '50px'}

hidden_dropdowns = {'marginRight':"25px",
                'marginLeft':"8px",
                "width" : "370px",
                'display': 'none',
                'marginBottom':'10px'}

visible_dropdowns = {'marginRight':"25px",
                'marginLeft':"8px",
                "width" : "370px",
                'marginBottom':'10px'}