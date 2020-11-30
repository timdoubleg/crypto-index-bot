    
    from binance.client import Client # Import the Binance Client
    from binance.websockets import BinanceSocketManager # Import the Binance Socket Manager

    # Although fine for tutorial purposes, your API Keys should never be placed directly in the script like below. 
    # You should use a config file (cfg or yaml) to store them and reference when needed.
    PUBLIC = 'r7NNoC9Y67xf2mmwSTYM1DwRA03Q3i6YHvKElp9aU6a3LFh0Fhmv0MRPSqBsAt6z'
    SECRET = 'CTfkY0bkUpiLfzEgZjL78X93UhN79Tb26Cqp7W27TSVvhod8vZUR3ACr1Q0B86ju'

    # Instantiate a Client 
    client = Client(api_key=PUBLIC, api_secret=SECRET)

    # Gets data from account balance as dictionary
    coin_balance = client.get_account()
    
    # Loops through the account balance and prints only the allocations > 0
    for element in coin_balance['balances']:
        if float(element.get('free')) > 0.00000000:
            print(str(element).replace("{","").replace("}","").replace("'",""))

