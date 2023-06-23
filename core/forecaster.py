from models.history import PriceHistory
from typing import Set


class Forecaster:
    def __init__(self) -> None:
        pass


    #  Takes in a set of tickets, a set of markets, a period of days, and interval
    # and forecasts the price of the stock based on the input.   
    def forecast_stock(self,ticker:str,market:str,days_out:int,interval:str = "1m") -> dict:
        forcasted_stock:dict = dict()

        # Returned dictionary 
        # {'ticker':{'old_close':int,'forecasted_close':int}}
        return forcasted_stock
    
    #  Takes in a set of tickets, a set of markets, a period of days, and interval
    # and forecasts the price of the stock based on the input.
    def forecast_stocks(self,stocks:Set[PriceHistory],markets:set = set(),days_out:int = 5, intervals:str = '1m') -> dict:
        forcasted_stocks:dict = dict()



        # Returned dictionary 
        # {'ticker':{'old_close':int,'forecasted_close':int}}
        return forcasted_stocks

    # Takes in a index and a set markets to find the underlying trend
    # represented in each market using moving averages
    def forecast_market_trend(index:Set[PriceHistory],market:str = '') -> dict:
        pass 

    # Takes in a stock ticker and will output the sentiment surrounding
    # the stock.
    def generate_stock_sentiment(ticker:PriceHistory) -> str:
        pass

    # Takes in a set stock tickers and will output the sentiment surrounding
    # the stocks.
    def generate_stock_sentiment(ticker:PriceHistory) -> str:
        pass

    # Takes in a set markets and will output the sentiment surrounding
    # the markets.
    def generate_market_sentiment(markets:set = set()) -> str:
        pass
        