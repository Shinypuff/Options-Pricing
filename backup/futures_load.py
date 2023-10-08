import pandas as pd

url = f'https://iss.moex.com/iss/engines/futures/markets/forts/securities.html'
url_to_check = "https://iss.moex.com/iss/statistics/engines/futures/markets/options/assets/KMU4/optionboard.html"
table = pd.read_html(url)
true_tickers = []
for i in table[0]["SECID (string:36)"]:
    check = pd.read_html(f"https://iss.moex.com/iss/statistics/engines/futures/markets/options/assets/{i}/optionboard.html")[0]
    if len(check)!=0:
        true_tickers.append(i)
        print(i)
pd.DataFrame(true_tickers).to_excel("true_futures_ids.xlsx", index=False)
#table[0]["SECID (string:36)"].to_excel("futures_ids.xlsx", index=False)