# Crypto Index Bot

**Building an automated TOP 10- index for your binance account in Python**

**Class:** *Programming with advanced computer languages*

**Supervisor:** Dr. Prof. Mario Silic

**Date:** 04.11.2020 - 18.12.2020

**Technology:** Python 3

**Authors:** Tim Graf, Marvin Scherer, Henri de Montpellier

## Table of contents
* [Description](#Description)
* [Installation](#Installation)
* [Sources](#Sources)


# Description:

This is the official code for a project in the course _"Programming with Advanced Computer Languages"_ at the University of St. Gallen (HSG). The code rebalances your assets on your binance account in order to reflect a crypto index. The index is based on the ten biggest cryptoccurencies by market capitalization. Therefore, running the code will rebalance your binance portfolio so that it mimics the corresponding weights of the top ten cryptocurrencies' market capitalization.


In order to do so, the code works as follows:

<<<<<<< HEAD
<<<<<<< HEAD
1) The project retrieves your asset's allocation data from your binance account.
=======
<<<<<<< Updated upstream
=======
>>>>>>> f8944c66eba82410189d56fb3483381e782d0d89
1) the project retrieves your asset's allocation data from your binance account.
* Firstly, the project retrieves your asset's allocation data from your binance account. 
<<<<<<< HEAD
>>>>>>> Stashed changes
>>>>>>> 0427e482ca489de76b4b309058b0b843b5ba62b8
=======
>>>>>>> f8944c66eba82410189d56fb3483381e782d0d89

2) The project retrieves the cryptocurrencies' prices from binance and the market capitalization data from https://www.coingecko.com.

3) The different targeted weights based on the ten biggest cryptocurrencies market capitalization are computed.

4) These targeted weights are compared to your current assets' allocation in your binance portfolio.
    
    ![alt text](/img.png)

<<<<<<< HEAD
<<<<<<< HEAD
5) Based on this comparison, the buy and sell orders are made so that your binance portfolio's assets are equally weighted as the top ten cryptocurrencies by market capitalization. However, some of the orders might be below the minimum quantity or the minimum value you can buy. This is mostly due to the important Bitcoin dominance of the market. Therefore, the code will propose you two possibilities ```Do you want to proceed with rebalancing? y/n``` 
=======
<<<<<<< Updated upstream
=======
>>>>>>> f8944c66eba82410189d56fb3483381e782d0d89
5) based on this comparison, the buy and sell orders are made so that your binance portfolio's assets are equally weighted as the top ten cryptocurrencies by market capitalization. However, some of the orders might be below the minimum quantity or the minimum value you can buy. This is mostly due to the important Bitcoin dominance of the market. Therefore, the code will propose you two possibilities ```Do you want to proceed with rebalancing? y/n``` 
* Finally, based on this comparison, the buy and sell orders are made so that your binance portfolio's assets are equally weighted as the top ten cryptocurrencies by market capitalization. However, some of the orders might be below the minimum notional value or the minimum quantity you can buy. This is mostly due to the Bitcoin dominance of the market. Therefore, the code will propose you two possibilities ```Do you want to proceed with rebalancing? y/n``` 
<<<<<<< HEAD
>>>>>>> Stashed changes
>>>>>>> 0427e482ca489de76b4b309058b0b843b5ba62b8
=======
>>>>>>> f8944c66eba82410189d56fb3483381e782d0d89

    1)  ```y``` will disregard the smaller coins allocation and rebalance the portfolio based on the coins that are buyable. (Please note that in that case your portfolio will not reflect the ten biggest cryptocurrencies and will disregard the smaller ones)

    2)  ```n``` will not place the orders so that you can import additional funds in order to have enough assets to enable your portfolio to reflect the top 10 cryptocurrencies' allocation.

# Assumption: 
The code assumes that you already have some cryptocurrencies on your binance account.
The code rebalances 95% of your assets in order to keep 5% for any transaction costs. However, you can change the threshold.

# Errors you may run into 
1. If you get the error "BinanceAPIException: APIError(code=-1013): Filter failure: minQty"
This error appears because you are trying to create an order with a quantity (in units of the crypto) lower than the minimun required.

2. Error "BinanceAPIException: APIError(code=-1013): Filter failure: MIN_NOTIONAL"
This error appears when your quantity * price is smaller than the min_notional

3. Error "BinanceAPIException: APIError(code=-1013): Filter failure: stepSize"
This error appears if your order is not in the decimal dimension as the stepSize

4. Error "BinanceAPIException: APIError(code=-1013): Filter failure: "LOT SIZE": 
This appears when either min qt, max qt, stepSize, or min notional is violated

Please have a look at https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md



# Installation
This project requires the following packages: pandas, python-binance, pycoingecko.

1) In order to run this project, install the required packages using the requirements.txt file: 
    ```
     pip3 freeze > requirements.txt
     pip3 install -r requirements.txt
    ```
2) Put your own "API_PUBLIC" and "API_SECRET" from your Binance Account in config.py and run config.py code. 
(Alternatively, you can use the keys already written in the file which are linked the creators of the code's own binance account)

# Sources
* Binance API documentation: https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md 
* Coingecko API documentation: https://www.coingecko.com/api/documentations/v3 


