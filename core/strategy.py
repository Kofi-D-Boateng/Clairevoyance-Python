from analyzer import MarketAnalyzer
from forecaster import Forecaster
from models.models import Portfolio,PriceHistory
from typing import Set

class Strategy:
    
    def __init__(self) -> None:
        pass

    def execute_arbitrage_strategy(self,portfolio:Portfolio, potential_stocks:Set[PriceHistory]):
        pass
    
    def execute_bollinger_band_strategy(self,portfolio:Portfolio, potential_stocks:Set[PriceHistory]):
        pass

    def execute_mean_reversion_strategy(self,portfolio:Portfolio, potential_stocks:Set[PriceHistory]):
        pass    

    def execute_momentum_strategy(self,portfolio:Portfolio, potential_stocks:Set[PriceHistory]):
        pass
    
    # WORK ON THIS FIRST
    def execute_moving_average_strategy(self,portfolio:Portfolio, potential_stocks:Set[PriceHistory], type:str):

        # 1. GET PORTFOLIO INFORMATION
        # 2. CALCULATE MOVING AVERAGE OF EACH POTENTIAL STOCK
        # 3. PERFORM MA STRATEGY TO SEE IF A BUY OR SELL IS BEING SIGNALED
        # 4A. CALCULATE PERCENTAGE OF PORTFOLIO WILLING TO RISK (~>= 10% of port.)
        # 4B. CHECK IF POTENTIAL STOCKS ARE ALREADY WITHIN YOUR HOLDINGS AS TO NOT
        #     OVERLEVERAGE PORTFOLIO.

        # Get the portfolio's total funds, current funds and the holdings
        curr_funds,total_funds,holdings = portfolio.get_current_funds(),portfolio.get_total_funds(),portfolio.get_holdings()
        for ticker in potential_stocks:
            print(f'[STATE]:Currently on ticker:{ticker}')
            # holdings is a dict where key = some ticker and value = another dictionary
            # The value dictionary will hold the total invested amount and total number of
            # shares. ---> {ticker:'GOOG',info:{shares:55,amount:$25,000}}
            if ticker in holdings:
                info:dict = holdings.get(ticker)
                shares,amount = info.get("shares"),info.get("amount")
                port_perc:float = (amount/total_funds)*100
                print(f"TICKER:{ticker} is {port_perc}% of the portfolio")

                
            else:
                print("")

    def execute_pairs_trading_strategy(self,portfolio:Portfolio, potential_stocks:Set[PriceHistory]):
        pass

    def execute_scalping_strategy(self,portfolio:Portfolio, potential_stocks:Set[PriceHistory]):
        pass