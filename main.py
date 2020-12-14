from pycoingecko import CoinGeckoAPI 
from binance.client import Client # Import the Binance Client
from binance.websockets import BinanceSocketManager # Import the Binance Socket Manager
import pandas as pd
import config

# The code has been checked for errors. The warning happens when a dataframe is overwritte. 
# Turn off warnings
pd.options.mode.chained_assignment = None  # default='warn'


cg = CoinGeckoAPI()

# Instantiate a Client 
client = Client(api_key=config.PUBLIC, api_secret=config.SECRET)

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
sum_caps = market_cap['market_cap_percentage'].sum() 
market_cap['market_cap_percentage'] = (market_cap['market_cap_percentage']/sum_caps)


# Get market data prices from coingecko
tickers = client.get_ticker()
prices = pd.DataFrame.from_dict(tickers)
prices_table_columns = ['symbol', 'lastPrice']
prices = prices.drop(columns=[col for col in prices if col not in prices_table_columns]) #drop all values not needed


# As USDTUSDT does not exist we need to append it
prices.loc[prices['symbol']=='USDTUSDT'] #check for USDT
prices = prices.append({'symbol': 'USDTUSDT', "lastPrice": 1}, ignore_index=True)
prices.loc[prices['symbol']=='USDTUSDT'] #check for USDT again, now we find it
print(prices)

# create columns for later and some more data handling
coin_balance['portfolio weights'] = 'NA'
coin_balance['USDT'] = 'NA'
coin_balance = coin_balance.rename(columns={'asset': 'symbol'}) #change name of column
coin_balance['symbol'] = coin_balance['symbol'] + 'usdt' # add USDT to string
coin_balance['symbol'] = coin_balance['symbol'].str.upper() # make the dataframe Uppercase to compare


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
df.loc[df['symbol'] == 'USDTUSDT'] #probably not necessary


# drop all not needed values from the df price 
df_table_columns = ['symbol', 'lastPrice', 'free', 'portfolio weights', 'USDT']
df = df.drop(columns=[col for col in df if col not in df_table_columns])
market_cap

#merge both dataframes
df_merged = pd.merge(df, market_cap, how ='left', on='symbol')
df_merged = df_merged.sort_values(by='market_cap_percentage', ascending=False, na_position='last') #sort by largest to smallest
df_merged['market_cap_percentage'] = df_merged['market_cap_percentage'].fillna(0)


#calculate the differences
df_merged['difference'] = df_merged['market_cap_percentage'] - df_merged['portfolio weights']

#compare market_cap_perc and df
print(market_cap)
df_merged = df_merged[(df_merged["free"] != 0) | (df_merged["market_cap_percentage"] != 0)]
print(df_merged)


# ------------------------

# Start placing orders






#without USDT
df_merged['symbol'] = df_merged['symbol'].str[:-4]








