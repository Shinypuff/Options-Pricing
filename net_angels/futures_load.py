import pandas as pd

url = f'https://iss.moex.com/iss/engines/futures/markets/forts/securities.html'
url_to_check = "https://iss.moex.com/iss/statistics/engines/futures/markets/options/assets/KMU4/optionboard.html"
table = pd.read_html(url)
true_tickers = []

for i in table[0]["SECID (string:36)"]:
    check = pd.read_html(f"https://iss.moex.com/iss/statistics/engines/futures/markets/options/assets/{i}/optionboard.html")[0]
    if len(check)!=0:
        true_tickers.append(i)
        print(true_tickers)

filter = table[0][table[0]["SECID (string:36)"].isin(true_tickers)]
print(filter)
#output = pd.DataFrame(columns=["SECID (string:36)", "ASSETCODE (string:75)"], data=(filter["SECID (string:36)"], filter["ASSETCODE (string:75)"]))
filter.to_excel("true_futures_ids.xlsx", index=False)
