# PWACL
Title: Building an automated index for your binance account in Python

Date: 04.11.2020 - 18.12.2020

Technology: Python 3.6

Authors: Tim Graf, Marvin Scherer, Henri de Montpellier

## Table of contents
* [Description](#Description)
* [Installation](#Installation)
* [Sources](#Sources)


# Description:

This is the official code for a project in the course "Programming with Advanced Computer Languages" at the University of St. Gallen. The codes aim at rebalancing your assets on your binance account in oreder to reflex our index. The index is based on the ten biggest cryptoccurencies by market capitalization. Therefore, running the code will rebalance your binance portfolio in order for it to be weighted according to the top ten cryptocurrencies' market capitalization.

Technology: Python 3.6

In order to do so, the code works as follows:

* Firstly, the project retrieves your asset's allocation data from your binance account.
* Secondly, the project retrieves market capitalization data and cryptocurrencies' prices from https://www.coingecko.com 
* Thirdly, the different targeted weights based on the ten biggest cryptocurrencies market capitalization are computed.
* Fourthly, these targeted weights are compared to your current assets' allocation in your binance portfolio. 
* Finally, based on this comparison, the buy and sell orders are made so that your binance portfolio's assets are equally weighted as the top ten cryptocurrencies by market capitalization.

## Assumption: 
The code assumes that you already have some cryptocurrencies on your binance account.
The code rebalances 90% of your assets in order to keep 10% for any transaction costs.

# Installation
This project requires the following packages: pandas, python-binance, pycoingecko.

1) In order to run this project, install the required packages using the requirements.txt file: 
    ```
    $ pip freeze > requirements.txt
    $ pip3 install -r requirements.txt
    ```
2) Put your own "API_KEY" and "API_SECRET" from your Binance Account in config.py and run config.py code. 
(Alternatively, you can use the keys already written in the file which are linked the creators of the code's own binance account)

# Sources
* Binance API documentation: https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md 
* Coingecko API documentation: https://www.coingecko.com/api/documentations/v3 


