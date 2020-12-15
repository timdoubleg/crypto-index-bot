from pycoingecko import CoinGeckoAPI 
# Import the Binance Client
from binance.client import Client 
# Import the Binance Socket Manager
from binance.websockets import BinanceSocketManager 
import pandas as pd
import config.py

# turn off warnings
## default='warn'
pd.options.mode.chained_assignment = None  

cg = CoinGeckoAPI()


# Instantiate a Client 
client = Client(api_key=config.api_key, api_secret=config.api_secret)

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
# get the data from the api
market_cap = pd.DataFrame.from_dict(cg.get_global())
#sort by largest to smallest
market_cap = market_cap.sort_values(by='market_cap_percentage', ascending=False, na_position='last')
# reset index
market_cap = market_cap.reset_index(drop=False)
#only get top 10
market_cap = market_cap.head(10)
#add columns
columns_marketcap = ['index', 'market_cap_percentage']
#drop all columns we don't need
market_cap = market_cap.drop(columns=[col for col in market_cap if col not in columns_marketcap])
#change name of column
market_cap = market_cap.rename(columns={'index': 'symbol'}) 
 # add USDT to string
market_cap['symbol'] = market_cap['symbol'] + 'usdt'
# make the dataframe Uppercase to compare
market_cap['symbol'] = market_cap['symbol'].str.upper() 
sum_caps = market_cap['market_cap_percentage'].sum() 
market_cap['market_cap_percentage'] = (market_cap['market_cap_percentage']/sum_caps)

"""
# COINGECKO: Get market cap data from 
tickers = client.get_ticker()
prices = pd.DataFrame.from_dict(tickers)
prices_table_columns = ['symbol']
prices = prices.drop(columns=[col for col in prices if col not in prices_table_columns]) #drop all values not needed
prices.loc[prices['symbol']=='BTCUSDT'] #check for USDT

# COINGECKO: As USDTUSDT does not exist we need to append it
prices.loc[prices['symbol']=='USDTUSDT'] #check for USDT
prices = prices.append({'symbol': 'USDTUSDT', "lastPrice": 1}, ignore_index=True)
prices.loc[prices['symbol']=='USDTUSDT'] #check for USDT again, now we find it
print(prices)
"""

# BINANCE: Get prices from Binance
#gets all prices
prices_binance = client.get_all_tickers() 
#converts dictionary to dataframe
prices_binance = pd.DataFrame.from_dict(prices_binance) 
#check for BTCUSDT, we find it
prices_binance.loc[prices_binance['symbol']=='BTCUSDT'] 

# As USDTUSDT does not exist we need to append it
#check for USDT
prices_binance.loc[prices_binance['symbol']=='USDTUSDT'] 
prices_binance = prices_binance.append({'symbol': 'USDTUSDT', "price": 1}, ignore_index=True)
#check for USDT again, now we find it
prices_binance.loc[prices_binance['symbol']=='USDTUSDT'] 
print(prices_binance)


# create columns for later and some more data handling
coin_balance['portfolio weights'] = 'NA'
coin_balance['USDT'] = 'NA'
#change name of column
coin_balance = coin_balance.rename(columns={'asset': 'symbol'}) 
# add USDT to string
coin_balance['symbol'] = coin_balance['symbol'] + 'usdt' 
# make the dataframe Uppercase to compare
coin_balance['symbol'] = coin_balance['symbol'].str.upper() 


# merge both dataframes
coin_balance = coin_balance.rename(columns={'asset': 'symbol'})
df = pd.merge(prices_binance, coin_balance, how ='inner', on='symbol')
#transform to integers
df['price'] = pd.to_numeric(df['price']) 
#check it is transformered to integers
df.dtypes 


# calculate portfolio values
for i in range(len(df)):
    df['USDT'][i] =  df['price'][i] * df['free'][i]

# calculate portfolio weights
df['USDT'] = pd.to_numeric(df['USDT'])
portfolio_sum = df['USDT']
portfolio_sum = portfolio_sum.sum()
for i in range(len(df)):
    df['portfolio weights'][i] = df['USDT'][i]/portfolio_sum
#probably not necessary
df.loc[df['symbol'] == 'USDTUSDT'] 


# drop all not needed values from the df price 
df_table_columns = ['symbol', 'price', 'free', 'portfolio weights', 'USDT']
df = df.drop(columns=[col for col in df if col not in df_table_columns])

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
# reset index
df_merged = df_merged.reset_index(drop=True) 

#change trading pairs from USDT to BTC with the exception of BTC, there we keep USDT
df_merged['symbol'] = df_merged['symbol'].str[:-4]
for i in range(len(df_merged)):
    if df_merged['symbol'][i] == 'USDT':
        df_merged['symbol'][i] = df_merged['symbol'][i]
    if df_merged['symbol'][i] == 'BTC':
        df_merged['symbol'][i] = df_merged['symbol'][i] + 'USDT'
    else:
        df_merged['symbol'][i] = df_merged['symbol'][i] + 'BTC'

print(df_merged)


# -------------------------------------------------------------

# Start placing orders
from binance.enums import *

#threshold as we need to account for fees
threshold = 0.95
i=0
pf_value = df_merged['USDT'].sum()

# get all open orders
print(client.get_all_orders(symbol=df_merged['symbol'][i]))
#if this is empty then we have no open orders

"""
# If we have USDT in our portfolio, we cannot sell directly USDT i, but we buy other cryptos with it
for i in range(len(df_merged)):
    if df_merged['symbol'][i] == 'USDTUSDT':
        print(df_merged['symbol'][i] + ': will not execute this order')
    else:
        print(df_merged['symbol'][i] + ': will execute this order')
"""

order = client.create_test_order(
    symbol='BNBBTC',
    side=SIDE_BUY,
    type=ORDER_TYPE_MARKET,
    quantity=100,
    price='0.001')

order = client.order_market_buy(
    symbol='BNBBTC',
    quantity=100)


# Single Test Order for ETHBTC
# creating a test order returns an empty response by design if the order would be valid (see the official docs). 
# You would get an error in the response if there were a problem with it, so the fact that your response is empty means success.
i=1
symbol = 'ETHBTC'
order = client.create_test_order(
    symbol=symbol,
    side=SIDE_BUY,
    type=ORDER_TYPE_MARKET,
    quantity=round(pf_value/df_merged['price'][i]*threshold*df_merged['difference'][i],3) 
)


# Single Test Order for ethbtc
i=2
symbol = 'XRPBTC'
order = client.create_test_order(
    symbol=symbol,
    side=SIDE_BUY,
    type=ORDER_TYPE_MARKET,
    quantity=round(pf_value/df_merged['price'][i]*threshold*df_merged['difference'][i],3) 
)



# Example for i=1 , eth
i=1
round(pf_value*threshold*df_merged['difference'][i],6) #how much USDT we need to sell
round(pf_value/df_merged['price'][i]*threshold*df_merged['difference'][i],6) #how much ETH we need to sell


# Extracting the minQty,stepSize, and minNotional to avoid errors: ---------------

info = client.get_symbol_info('ethbtc') 
#checks for the keys in the dictionary
for key in info:
    print(key, '->', info[key])
# transform filters to a dataframe
info_df = pd.DataFrame.from_dict(info['filters'])

index = seq(0,9)
columns = ['minQty', 'minNotional', 'StepSize']
filters = pd.DataFrame(index=index, columns=columns)

filters = pd.DataFrame(data=1)
#extract needed files 


# ERRORS: ---------------

info = client.get_symbol_info('ethbtc') 
# 1. If you get the error "BinanceAPIException: APIError(code=-1013): Filter failure: minQty"
# This error appears because you are trying to create an order with a quantity lower than the minimun required.
# Get minimum order amount
print('Minimum Order Amount: ' + info['filters'][2]['minQty'])

# 2. Error "BinanceAPIException: APIError(code=-1013): Filter failure: MIN_NOTIONAL"
# This error appears when your order amount is smaller than the cost
# Get minimum notional amount
print('Minimum Notional: ' + info['filters'][3]['minNotional'])

# 3. Error "LOT SIZE": This appears when either min qt, max qt, stepSize, or min notional is violated
# Get stepSiez
print('stepSize: ' + info['filters'][2]['stepSize'])




#-----------------------------------------
# For Loop for Rebalancing (Work in Progress)

for i in range(len(df_merged)):
    #sell order
    if df_merged['difference'][i] < 0:
        order = client.create_test_order(
            symbol= df_merged['symbol'][i],
            side=SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity = round(df_merged['difference'][i]*threshold*-1*pf_value,2)
            )
        print(df_merged['symbol'][i] + ': sell order')
        print(order)
    #buy order
    if df_merged['difference'][i] > 0:
        order = client.create_test_order(
            symbol= df_merged['symbol'][i],
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quantity = round(df_merged['difference'][i]*threshold*pf_value,2)
            )
        print(df_merged['symbol'][i] +': buy order')
        print(order)




order = client.create_order(
    symbol='BNBBTC',
    side=SIDE_BUY,
    type=ORDER_TYPE_LIMIT,
    timeInForce=TIME_IN_FORCE_GTC,
    quantity=100,
    price='0.00001')


#without USDT
df_merged['symbol'] = df_merged['symbol'].str[:-4]
"""




