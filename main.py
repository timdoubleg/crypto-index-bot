from pycoingecko import CoinGeckoAPI
from binance.client import Client 
from binance.websockets import BinanceSocketManager 
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
import pandas as pd
# Config.py is where you store your Binance API keys, make sure to add your own keys.
import config

# Turn off warnings test. The warning arises with pandas. The code has been checked and the warning is a false positive. 
# default = 'warn'
pd.options.mode.chained_assignment = None  

# You can change the threshold, we need it to account for fees
threshold = 0.95


# BINANCE -------------------------------------------------------

# Instantiate a Client 
client = Client(api_key=config.API_PUBLIC, api_secret=config.API_SECRET)

# Gets data from account balance as dictionary and transform to dataframe
coin_balance = client.get_account()
coin_balance = pd.DataFrame.from_dict(coin_balance['balances'])

# Transform values to integers and check if there are some assets in your binance account
try:
    coin_balance['free'] = pd.to_numeric(coin_balance['free'])
    coin_balance['locked'] = pd.to_numeric(coin_balance['locked'])
except:
    print("You do not have any assets in your binance account. Please deposit some coins in your account and run the code.")
    exit()

# Sort values after highest balance
coin_balance = coin_balance.sort_values(by = 'free', ascending = False, na_position = 'last')
print("User's Balance: \n", coin_balance)

# BINANCE: Get prices from Binance and convert it to a dataframe
prices_binance = client.get_all_tickers() 
prices_binance = pd.DataFrame.from_dict(prices_binance)

"""
# Get all open orders
print(client.get_all_orders(symbol=df_merged['symbol'][i]))
# If this is empty then we have no open orders. Else, if your user balance shows locked values, then you have open orders
"""


# COINGECKO ------------------------------------
cg = CoinGeckoAPI()

# Get market caps from coingecko API
market_cap = pd.DataFrame.from_dict(cg.get_global())

# Sort by largest to smallest
market_cap = market_cap.sort_values(by = 'market_cap_percentage', ascending = False, na_position = 'last')
market_cap = market_cap.reset_index(drop = False) 

# Only get top 10
market_cap = market_cap.head(10) 

# Initialize columns (market cap and symbol) and drop all columns we don't need 
columns_marketcap = ['index', 'market_cap_percentage'] 
market_cap = market_cap.drop(columns = [col for col in market_cap if col not in columns_marketcap]) 
market_cap = market_cap.rename(columns = {'index': 'symbol'}) 

# As we are searching for Trading Pairs with USDT, we append USDT to the end of the symbols
market_cap['symbol'] = market_cap['symbol'] + 'usdt' 
market_cap = market_cap.sort_values(by='market_cap_percentage', ascending=False, na_position='last')
market_cap = market_cap.reset_index(drop=True) 
market_cap['symbol'] = market_cap['symbol'].str.upper() 

# Calculate the Sums and adjust the market cap in order to get 100% for Top 10
sum_caps = market_cap['market_cap_percentage'].sum() 
market_cap['market_cap_percentage'] = (market_cap['market_cap_percentage']/sum_caps)


# DATA HANDLING -------------------------------------------------------------

# As the trading pair "USDTUSDT" does not exist we need manually to append it and set the value = 1
prices_binance = prices_binance.append({'symbol': 'USDTUSDT', "price": 1}, ignore_index=True)
# Check for USDT again, now we find it
# prices_binance.loc[prices_binance['symbol']=='USDTUSDT'] 

# Initialize columns (USDT and portfolio weights) and some more data handling
coin_balance['portfolio weights'] = 'NA'
coin_balance['asset_value_USDT'] = 'NA'
coin_balance = coin_balance.rename(columns={'asset': 'symbol'}) 

# Again: we are searching for Trading Pairs with USDT, we append USDT to the end of the symbols
coin_balance['symbol'] = coin_balance['symbol'] + 'usdt' 
coin_balance['symbol'] = coin_balance['symbol'].str.upper() 

# Merge the coin balance and the binance prices dataframes
coin_balance = coin_balance.rename(columns={'asset': 'symbol'})
df = pd.merge(prices_binance, coin_balance, how ='inner', on='symbol')
df['price'] = pd.to_numeric(df['price']) 
df = df.rename(columns={'price': 'price_USDT'}) 

# Calculate single price values
for i in range(len(df)):
    df['asset_value_USDT'][i] =  df['price_USDT'][i] * df['free'][i]

# Calculate total portfolio values in USDT and BTC 
df['asset_value_USDT'] = pd.to_numeric(df['asset_value_USDT'])
pf_value_usdt = df["asset_value_USDT"].sum()
index = df.query('symbol == "BTCUSDT"').index
price_btc = df['price_USDT'][index][0]
price_btc = float(price_btc)
pf_value_btc = pf_value_usdt/price_btc

# Calculate portfolio weights
for i in range(len(df)):
    df['portfolio weights'][i] = df['asset_value_USDT'][i]/pf_value_usdt

# Drop all not needed values from the dataframe 
df_table_columns = ['symbol', 'price_USDT', 'free', 'portfolio weights', 'asset_value_USDT']
df = df.drop(columns=[col for col in df if col not in df_table_columns])

# Merge the new dataframe with market cap and sort from largest to smallest
df_merged = pd.merge(df, market_cap, how ='left', on='symbol')
df_merged = df_merged.sort_values(by='market_cap_percentage', ascending=False, na_position='last') 
df_merged['market_cap_percentage'] = df_merged['market_cap_percentage'].fillna(0)

# Calculate the differences for rebalancing
df_merged['difference'] = df_merged['market_cap_percentage'] - df_merged['portfolio weights']

# Compare market_cap_perc and df
df_merged = df_merged[(df_merged["free"] != 0) | (df_merged["market_cap_percentage"] != 0)]
df_merged = df_merged.reset_index(drop=True) 
print("\nOverview of Assets and Rebalancing Differences: \n ", df_merged)

# Print portfolio values
print('Your USDT portfolio value is: ', pf_value_usdt)
print('Your BTC portfolio value is: ', pf_value_btc)


# BINANCE TRADING FILTERS - Extracting the minQty,stepSize, and minNotional to avoid errors: ---------------
print('\n')

# Create an empty dataframe
index = range(len(df_merged))
columns = ['symbol', 'minQty', 'minNotional', 'stepSize']
filters = pd.DataFrame(index=index, columns=columns)

# Run a loop to get all values for every currency
for i in range(len(df_merged)):
    
    symbol = df_merged['symbol'][i]

    if df_merged['symbol'][i] == 'USDTUSDT':
        # Leave USDTBTC as it is
        filters['symbol'][i] = symbol

    elif df_merged['symbol'][i] == "USDTBTC":
        # Change USDTBTC to BTCUSDT as the former doesn't exist as a trading pair
        symbol = 'BTCUSDT'

        # Get filter values 
        info = client.get_symbol_info(symbol) 

        # Extract needed files
        filters['symbol'][i] = symbol
        filters['minQty'][i] = info['filters'][2]['minQty']
        filters['minNotional'][i] = info['filters'][3]['minNotional']
        filters['stepSize'][i] = info['filters'][2]['stepSize']

    else:
        # Get filter values 
        info = client.get_symbol_info(symbol) 

        # Extract needed files 
        filters['symbol'][i] = symbol
        filters['minQty'][i] = info['filters'][2]['minQty']
        filters['minNotional'][i] = info['filters'][3]['minNotional']
        filters['stepSize'][i] = info['filters'][2]['stepSize']

#print("List of Filters for Binance Trading: \n", filters)


# Print the rebalancing process ----------------------------------------------------------------
print("\n Total USDT:",pf_value_usdt, "\n")

# For Loop that prints important information on executing the orders
n = 0
for i in range(len(df_merged)):
    n = n + 1
    coin_value = df_merged["difference"][i] * pf_value_usdt * threshold
    
    # Information for Buy Order
    if df_merged["difference"][i] > 0:
        print(n," BUY:", round(coin_value/df_merged["price_USDT"][i], 3), df_merged["symbol"][i],  "            Worth:" ,round(coin_value, 3), "USDT")
        # Accounting for filters
        if round(coin_value, 3) < float(filters["minNotional"][i]): 
            print("Your transaction must be at least", float(filters["minNotional"][i]), "USDT in order to be executed \n")
        else:
            print("\n")

    # Information for Sell Order
    else:   
        print(n," SELL:", round(abs(coin_value/df_merged["price_USDT"][i]), 3), df_merged["symbol"][i],  "            Worth:" ,abs(round(coin_value, 3)), "USDT")
        if abs(round(coin_value, 3)) < float(filters["minNotional"][i]): 
            print("Your transaction must be at least", float(filters["minNotional"][i]), "USD in order to be executed \n")
        else:
            print("\n")

"""
# ERRORS: use this for manual debugging ---------------------------------------

# Get the trading rules ('filters') from Binance and check for the keys in the dictionary
info = client.get_symbol_info('BTCUSDT') 
for key in info:
    print(key, '->', info[key])

# 1. If you get the error "BinanceAPIException: APIError(code=-1013): Filter failure: minQty"
# This error appears because you are trying to create an order with a quantity lower than the minimun required.
# Get minimum order amount
print('Minimum Order Amount: ' + info['filters'][2]['minQty'])

# 2. Error "BinanceAPIException: APIError(code=-1013): Filter failure: MIN_NOTIONAL"
# This error appears when your order amount is smaller than the cost
# Get minimum notional amount
print('Minimum Notional: ' + info['filters'][3]['minNotional'])

# 3. Error "BinanceAPIException: APIError(code=-1013): Filter failure: stepSize"
# This error appears if your order is not in the decimal dimension as the stepSize
print('stepSize: ' + info['filters'][2]['stepSize'])

# 4. Error "LOT SIZE": This appears when either min qt, max qt, stepSize, or min notional is violated
"""


# DATA HANDLING: Transform to numeric -------------------------------


# Exchange USDTBTC for the inverse as only BTCUSDT exists as a trading pair
df_merged['symbol'] = df_merged['symbol'].replace(['USDTBTC'],'BTCUSDT')
# Merge dataframes
df_merged = pd.merge(df_merged, filters, how ='left', on='symbol')
# Transform columns to numeric
df_merged['difference'] = pd.to_numeric(df_merged['difference'])
df_merged['portfolio weights'] = pd.to_numeric(df_merged['portfolio weights'])
df_merged['minQty'] = pd.to_numeric(df_merged['minQty'])
df_merged['minNotional'] = pd.to_numeric(df_merged['minNotional'])
df_merged['stepSize'] = pd.to_numeric(df_merged['stepSize'])
# Check for types
# df_merged.dtypes)

# Drop the row with USDT as we won't need it for testing/executing orders
index = df_merged.query('symbol == "USDTUSDT"').index[0]
df_merged = df_merged.drop(index=index)
df_merged = df_merged.reset_index(drop=True) 



# PLACING TEST ORDERS: For Loop for Rebalancing (Work in Progress) -----------------------------------------
print('\n')

# for i = 3 we have a scientific output for stepSize

print('Overview of outcomes when testing orders:')
for i in range(len(df_merged)):

    try:
        symbol = df_merged['symbol'][i]
        minNotional = df_merged['minNotional'][i]
        stepSize = df_merged['stepSize'][i]
        minQty = df_merged['minQty'][i]
        price = df_merged['price_USDT'][i]
        difference = df_merged['difference'][i]

        # how many do we buy?
        quantity = abs((pf_value_usdt * threshold * difference)/price)

        # round the decimals
        decimals = abs(int(f'{stepSize:e}'.split('e')[-1]))
        quantity = round(quantity, decimals)

        # Sell order
        if df_merged['difference'][i] < 0:
            order = client.create_test_order(
                symbol = symbol,
                side = SIDE_SELL,
                type = ORDER_TYPE_MARKET,
                quantity = quantity
                )
            print(df_merged['symbol'][i], ': succesful sell order: ', order)

        # Buy order
        elif df_merged['difference'][i] > 0:
            order = client.create_test_order(
                symbol = symbol,
                side = SIDE_BUY,
                type = ORDER_TYPE_MARKET,
                quantity = quantity
                )
            print(df_merged['symbol'][i], ': succesful buy order: ', order)

    except:  
        if quantity < minQty:
            print(symbol, ':', quantity, 'is smaller than minQty: ', minQty)
        if quantity*price < minNotional:
            print(symbol,  ':', round(quantity*price, decimals), 'is smaller than minNotional: ', minNotional)
        else:
            print(df_merged['symbol'][i] +': another error occured, please check manually!')


# PLACING ORDERS: For Loop for Rebalancing -----------------------------------------

print('\n Please check if the above code shows succesful orders. If not, not all orders might be executed')

while True: 
    try:
        answer = input('\n Do you want to proceed with the rebalancing?: y/n:  ')

        if answer == 'y':
            print('\n')
            for i in range(len(df_merged)):
                try:
                    # Set up the values
                    symbol= df_merged['symbol'][i]
                    minNotional = df_merged['minNotional'][i]
                    stepSize = df_merged['stepSize'][i]
                    minQty = df_merged['minQty'][i]
                    price = df_merged['price_USDT'][i]
                    difference = df_merged['difference'][i]

                    # How many do we buy?
                    quantity = abs((pf_value_usdt * threshold * difference)/price)

                    # Round the decimals
                    decimals = abs(int(f'{stepSize:e}'.split('e')[-1]))
                    quantity = round(quantity, decimals)

                    # Sell order
                    if df_merged['difference'][i] < 0:
                        order = client.order_market_sell(
                            symbol = symbol,
                            quantity = quantity
                            )
                        print(df_merged['symbol'][i], ': succesful sell order: ', order)

                    # Buy order
                    elif df_merged['difference'][i] > 0:
                        order = client.order_market_buy(
                            symbol= symbol,
                            quantity = quantity
                            )
                        print(df_merged['symbol'][i], ': succesful buy order: ', order)

                except:  
                    if quantity < minQty:
                        print(symbol, ':', quantity, 'is smaller than minQty: ', minQty)
                    if quantity*price < minNotional:
                        print(symbol,  ':', round(quantity*price, decimals), 'is smaller than minNotional: ', minNotional)
                    else:
                        print(df_merged['symbol'][i] +': another error occured, please check manually!')          
            break

        # If answer is no
        elif answer == 'n':
            print('\n Will not rebalance')
            break

        else: 
            print('please enter "y" or "n"')

    except:
        print('please enter "y" or "n"')