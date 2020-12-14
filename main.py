from pycoingecko import CoinGeckoAPI 
from binance.client import Client # Import the Binance Client
from binance.websockets import BinanceSocketManager # Import the Binance Socket Manager
import pandas as pd

cg = CoinGeckoAPI()

# Although fine for tutorial purposes, your API Keys should never be placed directly in the script like below. 
# You should use a config file (cfg or yaml) to store them and reference when needed.
PUBLIC = 'r7NNoC9Y67xf2mmwSTYM1DwRA03Q3i6YHvKElp9aU6a3LFh0Fhmv0MRPSqBsAt6z'
SECRET = 'CTfkY0bkUpiLfzEgZjL78X93UhN79Tb26Cqp7W27TSVvhod8vZUR3ACr1Q0B86ju'

# Instantiate a Client 
client = Client(api_key=PUBLIC, api_secret=SECRET)

# Gets data from account balance as dictionary
coin_balance = client.get_account()

# From dictionary to dataframe
coin_balance = pd.DataFrame.from_dict(coin_balance['balances'])

# Drops all the cryptocurrencies and leaves only the ones where we have money allocated
coin_balance["free"] = pd.to_numeric(coin_balance["free"], downcast="float")
coin_balance = coin_balance[coin_balance["free"] > 0]
print(coin_balance)

# Gets market caps
market_cap = pd.DataFrame.from_dict(cg.get_global())
market_cap_perc = market_cap["market_cap_percentage"].sort_values(ascending = False).head(10)
print(market_cap_perc)

# Computes the sum of all the percentages
total_market_cap = market_cap_perc.sum()
print(total_market_cap)




