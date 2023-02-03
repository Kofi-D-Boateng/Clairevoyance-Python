from forecaster import Forecaster
from models.models import Portfolio,PriceHistory
from typing import Set
from concurrent.futures import ThreadPoolExecutor
from math import floor

class Strategy:
    
    def __init__(self) -> None:
        pass

    def execute_arbitrage_strategy(self,portfolio:Portfolio, potential_stocks:Set[PriceHistory]):
        pass
    
    def execute_bollinger_band_strategy(self,portfolio:Portfolio, potential_stocks:Set[PriceHistory]):
        pass

    def execute_mean_reversion_strategy(self,portfolio:Portfolio, potential_stocks:Set[PriceHistory],type:str,window:float):
        numOfStocks = len(potential_stocks)
        executor:ThreadPoolExecutor = ThreadPoolExecutor(max_workers=numOfStocks)

        for ticker in potential_stocks:
            executor.submit(self.__mean_reversion_task(ticker,portfolio,type,window))
        executor.shutdown(wait=True)
    
    # WORK ON THIS FIRST
    def execute_moving_average_strategy(self,portfolio:Portfolio, potential_stocks:Set[PriceHistory], type:str,window:float):
        numOfStocks = len(potential_stocks)
        executor:ThreadPoolExecutor = ThreadPoolExecutor(max_workers=numOfStocks)

        for ticker in potential_stocks:
            executor.submit(self.__moving_average_task(ticker,portfolio,type,window))
        executor.shutdown(wait=True)

       
    def execute_pairs_trading_strategy(self,portfolio:Portfolio, potential_stocks:Set[PriceHistory]):
        pass

    def execute_scalping_strategy(self,portfolio:Portfolio, potential_stocks:Set[PriceHistory]):
        pass

    def __moving_average_task(self,ticker:PriceHistory,portfolio:Portfolio,type:str, window:float):
        pass


    def __mean_reversion_task(self,ticker:PriceHistory,portfolio:Portfolio,type:str, window:float):
        import pandas as pd
        # 1. GET PORTFOLIO INFORMATION
        # 2. CALCULATE MOVING AVERAGE OF EACH POTENTIAL STOCK
        # 3. PERFORM MA STRATEGY TO SEE IF A BUY OR SELL IS BEING SIGNALED
        # 4A. CALCULATE PERCENTAGE OF PORTFOLIO WILLING TO RISK (~>= 10% of port.)
        # 4B. CHECK IF POTENTIAL STOCKS ARE ALREADY WITHIN YOUR HOLDINGS AS TO NOT
        #     OVERLEVERAGE PORTFOLIO.

        # Get the portfolio's total funds, current funds and the holdings
        curr_funds,total_funds,holdings = portfolio.get_current_funds(),portfolio.get_total_funds(),portfolio.get_holdings()
        exposure_allowed = portfolio.get_max_exposure_allowed()
        print(f'[IN PROGRESS]:Currently on ticker:{ticker}')

        # holdings is a dict where key = some ticker and value = another dictionary
        # The value dictionary will hold the total invested amount and total number of
        # shares. ---> {ticker:'GOOG',info:{shares:55,amount:$25,000}}
        if ticker in holdings:
            info:dict = holdings.get(ticker)
            shares,amount = info.get("shares"),info.get("amount")
            print(f'Ticker:{ticker}, Shares:{shares}, Total amount: {amount}, Amount Per Share: {amount/shares}')
            port_perc:float = (amount/total_funds)*100

            if(port_perc >= exposure_allowed):
                print(f'The percentage of shares in your portfolio ({port_perc}) is greater than your max allowed exposure ({portfolio.get_max_exposure_allowed()})')
            
            else:
                print(f"TICKER:{ticker} is {port_perc}% of the portfolio")
                if(type == "ema"):
                    stock_df = pd.DataFrame(ticker.get_info())
                    stock_df[f'{window}-day ewma'] = stock_df["close"].ewm(span=window,adjust=False).mean()

                    for _,row in stock_df.iterrows():

                        price = row['close']
                        mov_avg = row[f'{window}-day ewma']


                else:
                    stock_df = pd.DataFrame(ticker.get_info())
                    stock_df[f'{window}-day ma'] = stock_df["close"].rolling(window=window).mean()

                    for _,row in stock_df.iterrows():
                        
                        price = row['close']
                        mov_avg = row[f'{window}-day ma']
            
        else:
            print(f'TICKER:{ticker} is {0}% of your portfolio. Calculating percentages....')
            if(type == "ema"):

                
                stock_df = pd.DataFrame(ticker.get_info())
                stock_df[f'{window}-day ewma'] = stock_df["close"].ewm(span=window,adjust=False).mean()
                buySellDict:dict = {}
                curr_price_total = 0.0
                curr_exposure:float = 0.0
                shares = 0
                # The derivative or rate of change between the stock
                # and its moving average.
                prev_roc = 0.0

                for _,row in stock_df.iterrows():

                    price = row['close']
                    mov_avg = row[f'{window}-day ewma']
                    curr_roc:float = abs(((price - mov_avg)/mov_avg)*100)

                    if price > mov_avg:
                        # We must calculate a threshold on what we want to constitute
                        # a buy into the long term and the short term.
                        if curr_exposure < exposure_allowed:

                            if(curr_roc < prev_roc):
                                # If triggered then we are contracting towards the mean (simple mean-reversion)
                                # We will go ahead and shedd shares for profit

                                # FIGURE OUT HOW MUCH WE WANT TO ACTUALLY SHED FOR PROFIT TAKING
                                shares_to_sell = floor((curr_price_total*curr_exposure)/(shares/curr_price_total))
                                if shares > 0 and shares - shares_to_sell >=0:
                                    shares -= shares_to_sell
                                else:
                                # BUYING IN (FIGURE OUT THRESH HOLD FOR MAKING PURCHASE)
                                    shares += 1
                                    curr_price_total += price
                                    curr_funds -= curr_price_total
                                    curr_exposure = (shares/total_funds)*100
                                    buySellDict[row['datetime']] = {"action":"buy","shares":shares - (shares-1)}
                                    

                        elif curr_exposure > exposure_allowed:
                            shares_to_sell = floor((curr_price_total*curr_exposure)/(shares/curr_price_total))
                            if(curr_roc < prev_roc):
                                # PROFIT TAKE
                                if shares > 0 and shares - shares_to_sell >=0:
                                    shares -= shares_to_sell




                    elif price < mov_avg:
                        # We must calculate a threshold on what we want to constitute
                        # a sell into the long term and the short term.
                        if shares > 0:
                            # Logic to determine how much to sell
                            # This triggers more selling
                            if curr_roc > prev_roc:
                                pass
                            # 

                            # This triggers a look into buying because of contraction
                            # within the derivative (i.e. the rate of change is slowing
                            # which signals a consolidation or reversation)
                            elif curr_roc < prev_roc:
                                # Look into logic for constituting a buy
                                pass

                
                
            else:
                import pandas as pd
                stock_df = pd.DataFrame(ticker.get_info())
                stock_df[f'{window}-day ma'] = stock_df["close"].rolling(window=window).mean()

                