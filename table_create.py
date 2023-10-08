import pandas as pd

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
tickers_list = tickers_table['asset (string:36)'].sort_values()
futures_filter = pd.read_excel("true_futures_ids.xlsx")
