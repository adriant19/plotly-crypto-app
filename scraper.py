from bs4 import BeautifulSoup
import requests
import json
import pandas as pd
import numpy as np


def load_data(currency):

    page = requests.get("https://coinmarketcap.com/")
    soup = BeautifulSoup(page.content, "html.parser")

    data = soup.find('script', id='__NEXT_DATA__', type='application/json')

    coin_data = json.loads(data.contents[0])
    listings = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']

    cols = listings[0]["keysArr"]
    rows = [r for r in listings[1:]]

    df = pd.DataFrame(np.array([n for n in listings[1:]], dtype=object), columns=cols+["Null"])

    df1 = df[[
        "slug",
        "symbol",
        f"quote.{currency}.price",
        f"quote.{currency}.percentChange1h",
        f"quote.{currency}.percentChange24h",
        f"quote.{currency}.percentChange7d",
        f"quote.{currency}.marketCap",
        f"quote.{currency}.volume24h"
    ]].rename(columns={
        "slug": "name",
        f"quote.{currency}.price": "price",
        f"quote.{currency}.percentChange1h": "1h%",
        f"quote.{currency}.percentChange24h": "24h%",
        f"quote.{currency}.percentChange7d": "7d%",
        f"quote.{currency}.marketCap": "market_cap",
        f"quote.{currency}.volume24h": "volume_24h"
    })

    df1.index = np.arange(1, len(df1) + 1)

    return df1
