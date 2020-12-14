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

#transform balance from dictionary to dataframe
coin_balance = pd.DataFrame.from_dict(coin_balance['balances'])
print(coin_balance)

# transform values to integers
coin_balance['free'] = pd.to_numeric(coin_balance['free'])
coin_balance['locked'] = pd.to_numeric(coin_balance['locked'])
coin_balance.dtypes

# Get market caps from coingecko
market_cap = pd.DataFrame.from_dict(cg.get_global()) #get the data from the api
market_cap = market_cap.sort_values(by='market_cap_percentage', ascending=False, na_position='last') #sort by largest to smallest
market_cap = market_cap.reset_index(drop=False) # reset index
market_cap = market_cap.head(10) #only get top 10
columns_marketcap = ['index', 'market_cap_percentage'] #add columns
market_cap = market_cap.drop(columns=[col for col in market_cap if col not in columns_marketcap]) #drop all columns we don't need
market_cap = market_cap.rename(columns={'index': 'symbol'}) #change name of column
market_cap['symbol'] = market_cap['symbol'] + 'usdt' # add USDT to string
market_cap['symbol'] = market_cap['symbol'].str.upper() # make the dataframe Uppercase to compare


# Get market data prices from coingecko
tickers = client.get_ticker()
prices = pd.DataFrame.from_dict(tickers)
coin_balance.loc[coin_balance['asset']=='USDTusdt']
#prices does not have a trading pair USDTUSDT


# create columns for later and some more data handling
coin_balance['portfolio weights'] = 'NA'
coin_balance['USDT'] = 'NA'
coin_balance['asset'] = coin_balance['asset'] + 'usdt' # add USDT to string
coin_balance['asset'] = coin_balance['asset'].str.upper() # make the dataframe Uppercase to compare

# merge both dataframes
coin_balance = coin_balance.rename(columns={'asset': 'symbol'})
df = pd.merge(prices, coin_balance, how ='inner', on='symbol')
df['lastPrice'] = pd.to_numeric(df['lastPrice']) #transform to integers
df.dtypes #check it is transformered to integers


# calculate portfolio values
for i in range(len(df)):
    df['USDT'][i] =  df['lastPrice'][i] * df['free'][i]

# calculate portfolio weights
df['USDT'] = pd.to_numeric(df['USDT'])
portfolio_sum = df['USDT']
portfolio_sum = portfolio_sum.sum()
for i in range(len(df)):
    df['portfolio weights'][i] = df['USDT'][i]/portfolio_sum
df

# drop all not needed values from the df price 
final_table_columns = ['symbol', 'lastPrice', 'free', 'portfolio weights', 'USDT']
df = df.drop(columns=[col for col in df if col not in final_table_columns])

# find USDT value (not needed)
coin_balance.loc[coin_balance['asset']=='USDTusdt']

#compare market_cap_perc and df
market_cap
df

#change index in market_cap to match the name in df
