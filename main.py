from pycoingecko import CoinGeckoAPI 
from binance.client import Client # Import the Binance Client
from binance.websockets import BinanceSocketManager # Import the Binance Socket Manager
import pandas as pd
import decimal 
import config
import binance.enums

# Turn off warnings test. The warning arrises with pandas. 
# The code has been checked and the warning is a false positive.
# default='warn'
pd.options.mode.chained_assignment = None  

# BINANCE ------------------------------------
# Although fine for tutorial purposes, your API Keys should never be placed directly in the script like below. 
# You should use a config file (cfg or yaml) to store them and reference when needed.
API_PUBLIC = 'r7NNoC9Y67xf2mmwSTYM1DwRA03Q3i6YHvKElp9aU6a3LFh0Fhmv0MRPSqBsAt6z'
API_SECRET = 'CTfkY0bkUpiLfzEgZjL78X93UhN79Tb26Cqp7W27TSVvhod8vZUR3ACr1Q0B86ju'

# Instantiate a Client 
client = Client(api_key=config.API_PUBLIC, api_secret=config.API_SECRET)

# Gets data from account balance as dictionary
coin_balance = client.get_account()

# Transform balance from dictionary to dataframe
coin_balance = pd.DataFrame.from_dict(coin_balance['balances'])
print("User's Balace: \n", coin_balance)

#Transform values to integers and check if there are some assets in your binance account
try:
    coin_balance['free'] = pd.to_numeric(coin_balance['free'])
    coin_balance['locked'] = pd.to_numeric(coin_balance['locked'])
    coin_balance.dtypes
except:
    print("You do not have any assets in your binance account. Please deposit some coins in your account and run the code.")
    exit()

# BINANCE: Get prices from Binance
prices_binance = client.get_all_tickers() 
# Converts dictionary to dataframe
prices_binance = pd.DataFrame.from_dict(prices_binance)
# Check for BTCUSDT, we find it
prices_binance.loc[prices_binance['symbol']=='BTCUSDT'] 

# COINGECKO ------------------------------------
cg = CoinGeckoAPI()

#Get market caps from coingecko
#Get the data from the api
market_cap = pd.DataFrame.from_dict(cg.get_global())
#sort by largest to smallest
market_cap = market_cap.sort_values(by='market_cap_percentage', ascending=False, na_position='last')
#reset index
market_cap = market_cap.reset_index(drop=False) 
#only get top 10
market_cap = market_cap.head(10) 
#Add columns
columns_marketcap = ['index', 'market_cap_percentage'] 
market_cap = market_cap.drop(columns=[col for col in market_cap if col not in columns_marketcap]) #drop all columns we don't need
market_cap = market_cap.rename(columns={'index': 'symbol'}) #change name of column
market_cap['symbol'] = market_cap['symbol'] + 'usdt' # add USDT to string
market_cap['symbol'] = market_cap['symbol'].str.upper() # make the dataframe Uppercase to compare
sum_caps = market_cap['market_cap_percentage'].sum() 
market_cap['market_cap_percentage'] = (market_cap['market_cap_percentage']/sum_caps)


# DATA HANDLING -------------------------------------------------------------

# As USDTUSDT does not exist we need to append it
prices_binance.loc[prices_binance['symbol']=='USDTUSDT'] # Check for USDT
prices_binance = prices_binance.append({'symbol': 'USDTUSDT', "price": 1}, ignore_index=True)
prices_binance.loc[prices_binance['symbol']=='USDTUSDT'] # Check for USDT again, now we find it
print("List of Prices: \n", prices_binance)

# Create columns for later and some more data handling
coin_balance['portfolio weights'] = 'NA'
coin_balance['USDT'] = 'NA'
coin_balance = coin_balance.rename(columns={'asset': 'symbol'}) # Change name of column
coin_balance['symbol'] = coin_balance['symbol'] + 'usdt' # Add USDT to string
coin_balance['symbol'] = coin_balance['symbol'].str.upper() # Make the dataframe Uppercase to compare

# Merge both dataframes
coin_balance = coin_balance.rename(columns={'asset': 'symbol'})
df = pd.merge(prices_binance, coin_balance, how ='inner', on='symbol')
# Transform to integers
df['price'] = pd.to_numeric(df['price']) 
# Check it is transformered to integers
# print(df.dtypes) 


# Calculate portfolio values
for i in range(len(df)):
    df['USDT'][i] =  df['price'][i] * df['free'][i]

# Calculate portfolio weights
df['USDT'] = pd.to_numeric(df['USDT'])
portfolio_sum = df['USDT']
portfolio_sum = portfolio_sum.sum()
for i in range(len(df)):
    df['portfolio weights'][i] = df['USDT'][i]/portfolio_sum

# Drop all not needed values from the df price 
df_table_columns = ['symbol', 'price', 'free', 'portfolio weights', 'USDT']
df = df.drop(columns=[col for col in df if col not in df_table_columns])

# Merge both dataframes
df_merged = pd.merge(df, market_cap, how ='left', on='symbol')
# Sort by largest to smallest
df_merged = df_merged.sort_values(by='market_cap_percentage', ascending=False, na_position='last') 
df_merged['market_cap_percentage'] = df_merged['market_cap_percentage'].fillna(0)

# Merge binance prices with our main df
df_merged = pd.merge(df_merged, prices_binance, on='symbol', how='left')

# calculate prices_USDT and prices_BTC
# change name of column
df_merged = df_merged.rename(columns={'price_x': 'price_USDT', 'price_y': 'price_BTC'}) 
index = df_merged.query('symbol == "BTCUSDT"').index
price_btc = df_merged['price_BTC'][index][0]
price_btc = float(price_btc)
df_merged['price_BTC'] = pd.to_numeric(df_merged['price_BTC'])
df_merged['price_BTC'] = df_merged['price_BTC']/price_btc

# Calculate the differences
df_merged['difference'] = df_merged['market_cap_percentage'] - df_merged['portfolio weights']

# Compare market_cap_perc and df
print("List of Market Caps: \n", market_cap)
df_merged = df_merged[(df_merged["free"] != 0) | (df_merged["market_cap_percentage"] != 0)]
print("\nRebalancing: \n ", df_merged)
# Reset index
df_merged = df_merged.reset_index(drop=True) 

# Calculate total pf values
pf_value_usdt = df_merged["USDT"].sum()
# Calculate the total portfolio value in btc
pf_value_btc = pf_value_usdt/price_btc

# Print portfolio values
print('\n')
print('Your USDT portfolio value is: ', pf_value_usdt)
print('Your BTC portfolio value is: ', pf_value_btc)

# REBALANCING - Printing the Rebalancing process orders -------------------------------------------------------------

# Threshold as we need to account for fees
threshold = 0.95

"""
# Get all open orders
print(client.get_all_orders(symbol=df_merged['symbol'][i]))
# If this is empty then we have no open orders
"""

# Print the rebalancing process
print("\n Total USD:",pf_value_usdt, "\n")

n = 0
for element in range(len(df_merged)):
    n = n + 1
    if df_merged["difference"][element] > 0:
        coin_value = df_merged["difference"][element] * pf_value_usdt
        print(n," Buy " , round(coin_value, 3), "USD worth of" ,df_merged["symbol"][element])
    else:
        coin_value = df_merged["difference"][element] * pf_value_usdt
        print(n," Sell " , round(abs(coin_value), 3), "USD worth of" ,df_merged["symbol"][element])


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
        #leave USDTBTC as it is
        filters['symbol'][i] = symbol
    elif df_merged['symbol'][i] == "USDTBTC":
        #change USDTBTC to BTCUSDT
        symbol = 'BTCUSDT'
        # get filter values 
        info = client.get_symbol_info(symbol) 

        # extract needed files
        filters['symbol'][i] = symbol
        filters['minQty'][i] = info['filters'][2]['minQty']
        filters['minNotional'][i] = info['filters'][3]['minNotional']
        filters['stepSize'][i] = info['filters'][2]['stepSize']
    else:
        # get filter values 
        info = client.get_symbol_info(symbol) 

        # extract needed files 
        filters['symbol'][i] = symbol
        filters['minQty'][i] = info['filters'][2]['minQty']
        filters['minNotional'][i] = info['filters'][3]['minNotional']
        filters['stepSize'][i] = info['filters'][2]['stepSize']

print(filters)


# DATA HANDLING: Transform to numeric -------------------------------
print('\n')


# exchange USDTBTC for the inverse as only BTCUSDT exists as a trading pair
df_merged['symbol'] = df_merged['symbol'].replace(['USDTBTC'],'BTCUSDT')
# merge dataframes
df_merged = pd.merge(df_merged, filters, how ='left', on='symbol')
#transform columns to numeric
df_merged['difference'] = pd.to_numeric(df_merged['difference'])
df_merged['portfolio weights'] = pd.to_numeric(df_merged['portfolio weights'])
df_merged['minQty'] = pd.to_numeric(df_merged['minQty'])
df_merged['minNotional'] = pd.to_numeric(df_merged['minNotional'])
df_merged['stepSize'] = pd.to_numeric(df_merged['stepSize'])
#check for types
#df_merged.dtypes)


# TESTING - MANUAL - BINANCE FILTERS: Test if minQty, minNotional and account for the stepSize -------------------------------
print('\n')


i = 2
symbol= df_merged['symbol'][i]
minNotional = df_merged['minNotional'][i]
stepSize = df_merged['stepSize'][i]
minQty = df_merged['minQty'][i]
price = df_merged['price_USDT'][i]
difference = df_merged['difference'][i]

# how many do we buy?
quantity = abs(pf_value_usdt * difference * threshold)

# round the decimals
decimals = abs(int(f'{stepSize:e}'.split('e')[-1]))
quantity = round(quantity, decimals)

# run the tests
if quantity < minQty:
    print(symbol, quantity, 'is smaller than minQty: ', minQty)
if quantity*price < minNotional:
    print(symbol, quantity*price, 'is smaller than minNotional: ', minNotional)
else:
    print(symbol, ' passed all tests')

# Test order BUY
try: 
    if df_merged['difference'][i] > 0:
        order = client.create_test_order(
                symbol= symbol,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity = quantity
                )

        print(df_merged['symbol'][i], ': BUY order: ', order)

    # Test order SELL
    elif df_merged['difference'][i] < 0:
        order = client.create_test_order(
                symbol= symbol,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity = quantity
                )
        print(df_merged['symbol'][i], ': SELL order: ', order)
except:
    print('there is an error with', symbol, 'please check it manually')



# TESTING - FOR LOOP - BINANCE FILTERS: Test if minQty, minNotional and account for the stepSize -------------------------------
print('\n')

for i in range(len(df_merged)):
    try: 
        symbol= df_merged['symbol'][i]
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

        # run the tests
        if quantity < minQty:
            print(symbol, quantity, 'is smaller than minQty: ', minQty)
        if quantity*price < minNotional:
            print(symbol, quantity*price, 'is smaller than minNotional: ', minNotional)
        else:
            print(symbol, ' passed all tests')
    except:
        print('error, something else went wrong')

"""
        # Test order BUY
        if df_merged['difference'][i] > 0:
            order = client.create_test_order(
                    symbol= symbol,
                    side=SIDE_BUY,
                    type=ORDER_TYPE_MARKET,
                    quantity = quantity
                    )

            print(df_merged['symbol'][i], ': BUY order: ', 'quantity :', quantity, order)

        # Test order SELL
        elif df_merged['difference'][i] < 0:
            order = client.create_test_order(
                    symbol= symbol,
                    side=SIDE_SELL,
                    type=ORDER_TYPE_MARKET,
                    quantity = quantity
                    )

            print(df_merged['symbol'][i], ': SELL order: ', 'quantity :', quantity, order)
"""


"""
# ERRORS: for manual debugging ---------------
print('\n')

#checks for the keys in the dictionary
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

# 3. Error "LOT SIZE": This appears when either min qt, max qt, stepSize, or min notional is violated
# Get stepSize
print('stepSize: ' + info['filters'][2]['stepSize'])

"""


"""
# PLACING ORDERS: For Loop for Rebalancing (Work in Progress) -----------------------------------------
print('\n')

# for i = 3 we have a scientific output for stepSize

for i in range(len(df_merged)):

    try:
        symbol= df_merged['symbol'][i]
        minNotional = df_merged['minNotional'][i]
        stepSize = df_merged['stepSize'][i]
        minQty = df_merged['minQty'][i]
        price = df_merged['price'][i]
        #if we have a stepSize of 1 we want to round to 0 decimals, else we want to round to a max of 3 decimals
        if stepSize == 1:
            round_value = 0
        elif stepSize != 1:
            round_value = str(stepSize)
            round_value = round_value[::-1].find('.')
        round_value = min(round_value,3)
        quantity = abs(round(df_merged['difference'][i]*threshold*pf_value_btc,round_value))

        # Sell order
        if df_merged['difference'][i] < 0:
            order = client.create_test_order(
                symbol= symbol,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity = quantity
                )
            print(df_merged['symbol'][i], ': sell order: ', order)

        # Buy order
        elif df_merged['difference'][i] > 0:
            order = client.create_test_order(
                symbol= symbol,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity = quantity
                )
            print(df_merged['symbol'][i], ': buy order: ', order)

    except:  
        print(df_merged['symbol'][i] +': error did not work')

"""