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
* [Errors you may encounter](#Errorsyoumayencounter)
* [Sources](#Sources)
* [Disclaimer](#Disclaimer)

# Description

This is the official code for a project in the course _"Programming with Advanced Computer Languages"_ at the University of St. Gallen (HSG). The code rebalances your assets on your binance account in order to reflect a crypto index. The index is based on the ten biggest cryptoccurencies by market capitalization. Therefore, running the code will rebalance your binance portfolio so that it mimics the corresponding weights of the top ten cryptocurrencies' market capitalization.


In order to do so, the code works as follows:

1) Asset's allocation data are retrieved from your binance account.

2) Cryptocurrencies' prices are pulled from binance and the market capitalization data from https://www.coingecko.com.

3) The target weights are computed based on the top ten cryptocurrencies by market cap.

4) These target weights are compared to your current assets' allocation in your binance portfolio.
    
    ![alt text](/img.png)

5) Based on this comparison, the buy and sell orders are made so that your binance portfolio's assets are weighted as the top ten cryptocurrencies by market capitalization. However, some of the orders might be below the minimum quantity or the minimum notional value you can buy. This is mostly due to the Bitcoin dominance of the market. For instance, on 18.12.20 Bitcoin has a market cap of 64%, while the smallest coin in our top ten index (BNB) has 0.7%.

Hence, the code will propose you two possibilities ```Do you want to proceed with rebalancing? y/n``` 

    1)  ```y``` will disregard the smaller coins allocation and rebalance the portfolio based on the coins that you are able to buy within the trading rules of Binance. (Please note that in that case your portfolio will not reflect the ten biggest cryptocurrencies and will disregard the smaller ones)

    2)  ```n``` will not place the orders so that you can deposit additional funds in order to have enough assets to enable your portfolio to reflect the top 10 cryptocurrencies' allocation.

## Assumptions
The code assumes that you already have some cryptocurrencies on your binance account.
The code rebalances 95% of your assets in order to keep 5% for any transaction costs. However, you can change the threshold.   

# Installation
This project requires the following packages: pandas, python-binance, pycoingecko.

1) In order to run this project, install the required packages using the requirements.txt file: 
    ```
     pip3 freeze > requirements.txt
     pip3 install -r requirements.txt
    ```
2) Put your own "API_PUBLIC" and "API_SECRET" from your Binance Account in config.py and run config.py code. 
(Alternatively, you can use the keys already written in the file which are linked the creators of the code's own binance account)



# Errors you may encounter 
1. If you get the error "BinanceAPIException: APIError(code=-1013): Filter failure: minQty"
This error appears because you are trying to create an order with a quantity (in units of the crypto) lower than the minimun required.

2. Error "BinanceAPIException: APIError(code=-1013): Filter failure: MIN_NOTIONAL"
This error appears when your quantity * price is smaller than the min_notional

3. Error "BinanceAPIException: APIError(code=-1013): Filter failure: stepSize"
This error appears if your order is not in the decimal dimension as the stepSize

4. Error "BinanceAPIException: APIError(code=-1013): Filter failure: "LOT SIZE": 
This appears when either min qt, max qt, stepSize, or min notional is violated

Please have a look at https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md


# Sources
* Binance API documentation: https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md 
* Coingecko API documentation: https://www.coingecko.com/api/documentations/v3 

# Disclaimer 

The information in this repository is for educational purposes only and is not investment or financial advice. Please do your own research before making any investment decisions. None of the information in this repository constitutes, or should be relied on as, a suggestion, offer, or other solicitation to engage in, or refrain from engaging in, any purchase, sale, or any other any investment-related activity with respect to any ICO or other transaction. Cryptocurrency investments are volatile and high risk in nature. Don't invest more than what you can afford to lose.




