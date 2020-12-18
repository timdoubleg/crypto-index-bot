# PWACL
Title: Building an automated index for your binance account in Python

Date: 04.11.2020 - 18.12.2020

Technology: Python 3

Authors: Tim Graf, Marvin Scherer, Henri de Montpellier

## Table of contents
* [Description](#Description)
* [Installation](#Installation)
* [Sources](#Sources)


# Description:

This is the official code for a project in the course "Programming with Advanced Computer Languages" at the University of St. Gallen. The codes aim at rebalancing your assets on your binance account in order to reflect our index. The index is based on the ten biggest cryptoccurencies by market capitalization. Therefore, running the code will rebalance your binance portfolio so that it mimics the corresponding weights of the top ten cryptocurrencies' market capitalization.


In order to do so, the code works as follows:

* Firstly, the project retrieves your asset's allocation data from your binance account.

* Secondly, the project retrieves the cryptocurrencies' prices from binance and the market capitalization data from https://www.coingecko.com. As follows:

![](/.png)

* Thirdly, the different targeted weights based on the ten biggest cryptocurrencies market capitalization are computed.

* Fourthly, these targeted weights are compared to your current assets' allocation in your binance portfolio. As follows:

![](/Adjusted_MC.png)

* Finally, based on this comparison, the buy and sell orders are made so that your binance portfolio's assets are equally weighted as the top ten cryptocurrencies by market capitalization. However, some of the orders might be below the minimum quantity or the minimum value you can buy. This is mostly due to the important Bitcoin dominance of the market. Therefore, the code will propose you two possibilities ```Do you want to proceed with rebalancing? y/n``` 

1)  ```y``` will disregard the smaller coins allocation and rebalance the portfolio based on the coins that are buyable. (Please note that in that case your portfolio will not reflect the ten biggest cryptocurrencies and will disregard the smaller ones)

2)  ```n``` The code will not place the orders so that you can import additional funds in order to have enough assets to enable your portfolio to reflect the top 10 cryptocurrencies' allocation.

## Assumption: 
The code assumes that you already have some cryptocurrencies on your binance account.
The code rebalances 95% of your assets in order to keep 10% for any transaction costs.


# Installation
This project requires the following packages: pandas, python-binance, pycoingecko.

1) In order to run this project, install the required packages using the requirements.txt file: 
    ```
    $ pip3 freeze > requirements.txt
    $ pip3 install -r requirements.txt
    ```
2) Put your own "API_KEY" and "API_SECRET" from your Binance Account in config.py and run config.py code. 
(Alternatively, you can use the keys already written in the file which are linked the creators of the code's own binance account)

# Sources
* Binance API documentation: https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md 
* Coingecko API documentation: https://www.coingecko.com/api/documentations/v3 


