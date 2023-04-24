from models.models import Portfolio,PriceHistory,Candle
from enums.enums import TradeSignal,MovingAverageType,IntervalType
from typing import Set,List,Tuple,Any
import pandas
from concurrent.futures import ThreadPoolExecutor, Future
from math import floor

class TradeRecord:
    """
    The TradeRecord class is used to keep track of decisions made during the 
    execution of the strategy. We will use this class wihtin the Strategy
    class to keep a record for our back tester, where we will print out
    the record to allow for more decisions to be made.
    """
    choice: TradeSignal
    price: float
    datetime: float
    def __init__(self,choice: TradeSignal,price: float,date: float) -> None:
        self.choice = choice
        self.price = price
        self.datetime = date

class Strategy:
    """
    The Strategy Class contains all the strategies you can use to predict to buy, sold, or hold a stock.
    """
    record_list: List[TradeRecord]
    
    def __init__(self) -> None:
        self.record_list = list()
    ################################################################# HELPER FUNCTIONS ##################################################################################################


    ################################################################# PUBLIC FUNCTIONS ##################################################################################################

    def execute_arbitrage_strategy(self,potential_stocks:Set[PriceHistory]):
        pass
    
    def execute_bollinger_band_strategy(self,potential_stocks: List[PriceHistory],type: MovingAverageType, window: float, std: int) -> List[Tuple[PriceHistory,TradeSignal]]:
        numOfStocks = len(potential_stocks)
        executor:ThreadPoolExecutor = ThreadPoolExecutor(max_workers=numOfStocks)
        futures: List[Future[TradeSignal]] = []
        for ticker in potential_stocks:
            futures.append(executor.submit(self.__bollinger_band_task(ticker,type,window, std)))
        executor.shutdown(wait=True)

        trading_results: List[Tuple[PriceHistory,TradeSignal]] = []

        for i in range(0,len(futures)):
            trading_results.append((potential_stocks[i],futures[i].result()))

        return trading_results 

    def execute_mean_reversion_strategy(self,potential_stocks:List[PriceHistory],type: MovingAverageType,window:float) -> List[Tuple[PriceHistory,TradeSignal]]:
        numOfStocks = len(potential_stocks)
        executor:ThreadPoolExecutor = ThreadPoolExecutor(max_workers=numOfStocks)
        futures: List[Future[TradeSignal]] = []
        for ticker in potential_stocks:
            futures.append(executor.submit(self.__mean_reversion_task(ticker,type,window)))
        executor.shutdown(wait=True)

        trading_results: List[Tuple[PriceHistory,TradeSignal]] = []

        for i in range(0,len(futures)):
            trading_results.append((potential_stocks[i],futures[i].result()))

        return trading_results 
    
    def execute_moving_average_strategy(self,potential_stocks:List[PriceHistory], type: MovingAverageType,window: int) -> List[Tuple[PriceHistory,TradeSignal]]:
        numOfStocks = len(potential_stocks)
        executor:ThreadPoolExecutor = ThreadPoolExecutor(max_workers=numOfStocks)
        futures: List[Future[TradeSignal]] = []
        for ticker in potential_stocks:
            futures.append(executor.submit(self.__moving_average_task(ticker,type,window)))
        executor.shutdown(wait=True)

        trading_results: List[Tuple[PriceHistory,TradeSignal]] = []

        for i in range(0,len(futures)):
            trading_results.append((potential_stocks[i],futures[i].result()))

        return trading_results    
 
    def execute_pairs_trading_strategy(self,stock_pairs_list: List[Tuple[PriceHistory,PriceHistory]]) -> List[Tuple[Tuple[PriceHistory,PriceHistory],TradeSignal]]:
        numOfStocks = len(stock_pairs_list)
        executor:ThreadPoolExecutor = ThreadPoolExecutor(max_workers=numOfStocks)
        futures: List[Future[TradeSignal]] = []
        for pair in stock_pairs_list:
            futures.append(executor.submit(self.__pairs_trading_task(pair)))
        executor.shutdown(wait=True)

        trading_results: List[Tuple[Tuple[PriceHistory,PriceHistory],TradeSignal]] = []

        for i in range(0,len(futures)):
            trading_results.append((stock_pairs_list[i],futures[i].result()))

        return trading_results    

    def execute_scalping_strategy(self,potential_stocks:Set[PriceHistory]):
        pass

    def __pairs_trading_task(self, stock_pair: Tuple[PriceHistory,PriceHistory]) -> TradeSignal:
        pass

    def __bollinger_band_task(self,ticker: PriceHistory,type: MovingAverageType,window: float, std: int) -> TradeSignal:
        pass

    def __moving_average_task(self,ticker: PriceHistory,type: MovingAverageType, window: int) -> TradeSignal:
        # Set up variables
        signal:TradeSignal = TradeSignal.HOLD
        average_window = window 
        resample = False
        candles: List[Candle] = ticker.get_info()
        data:List[dict[str, Any]] = []
        keys = {
            "exponential":f'{window}-day ema',
            "simple":f'{window}-day ma',
            'std': 'stardard-deviation',
            'avg-std': 'average standard-deviation',
            'cv': 'coefficient of variance'
        }
        for candle in candles:
            data.append({
                'open': candle.open,
                'close': candle.close,
                'low': candle.low,
                'high': candle.high,
                'volume': candle.volume,
                'date': candle.date
            })
        
        candles_df: pandas.DataFrame = pandas.DataFrame(data)

        # Calculate averages
        """
        During this phase, we need to check the stock data to correctly calulate our statistics.
        From here, we can use a switch statement based on the case of the IntervalType of the stock.
        This will dictate how many data points per window should be used to calulate our stats. We
        also need to normalize.

        For example, the rolling method lends itself better for data points marked in singles (n-days
        n-weeks). We could possibly have a chart that is a 3 month chart that is split on 15 minutes
        intervals. This is when we would normalize our interval datas to be able to pick up the correct
        points:

        For a 20 day rolling mean on a 3 month 15-min chart:
            1-Trading Day |     32.5hrs     | 60 Trading Days  
            --------------|-----------------|----------------   
                6.5hrs    | 5 Trading Days  |  390 hours
        
        Without accounting for holidays we have 3months =~ 390hrs of non-crypto/futures/forex trading (equity).
        each ticker = 15minutes, therefore 30 minutes = a two ticker normalization.
        This means we need 13 30min segments X 2 tickers = 26 tickers for each trading period.
        (We will normalize to 30 minutes to make it easier to match trading periods when intervals >= 30min)
        26*60 days = 1560 tickers/20 = 1200 (so our window would be 1200 when resampling or using rolling)
        """

        candles_df.set_index('date',inplace=True)

        if ticker.get_interval_type().value == IntervalType.SECOND.value:
            day_in_seconds = 1 * 24 * 60 * 60 # 86,4000sec/1day
            day_in_seconds *= average_window # normalizing window in days to seconds in days
            average_window = day_in_seconds/ticker.get_interval() # window represents number of tickers needed to be added to represent
            pass
        elif ticker.get_interval_type().value == IntervalType.MINUTE.value:
            day_in_minutes = 1 * 24 * 60
            day_in_minutes *= average_window
            average_window /= ticker.get_interval()
        elif ticker.get_interval_type().value == IntervalType.HOUR.value:
            day_in_hours = 24
            day_in_hours *= average_window
            day_in_hours /= ticker.get_interval()
        elif ticker.get_interval_type().value == IntervalType.DAY.value:
            average_window /= ticker.get_interval()
        elif ticker.get_interval_type().value == IntervalType.MONTH or ticker.get_interval_type().value == IntervalType.QUARTER.value or ticker.get_interval_type().value == IntervalType.YEAR.value:
            resample = True
        else:
            print("[ERROR]: Could not determine course of action against interval type....")
            return

        if type == MovingAverageType.EXPONENTIAL:
            if resample:
                candles_df = candles_df.resample(ticker.get_interval_type().name).last()

            candles_df[keys['exponential']] = candles_df[keys['close']].rolling(window=average_window).mean()
        else:
            if resample:
                candles_df = candles_df.resample(ticker.get_interval_type().name).last()

            candles_df[keys['simple']] = candles_df['close'].ewm(span=average_window,adjust=False).mean()
        
        # Calculate standard deviation and the average standard deviation over the time series
        candles_df[keys['std']] = candles_df['close'].sub(candles_df[keys['exponential'] if type == MovingAverageType.EXPONENTIAL else keys['simple']]).abs().rolling(window=average_window).std()
        candles_df[keys['cv']] = (candles_df[keys['std']]/candles_df[keys['exponential'] if type == MovingAverageType.EXPONENTIAL else keys['simple']])

        for _,row in candles_df.iterrows():
            close_price = row['close']
            average_price = row[keys['exponential'] if type == MovingAverageType.EXPONENTIAL else keys['simple']]
            cv = row[keys['cv']]

            if average_price != 0:
                """
                Once we have a average to compare against, we will follow these next steps
                1. Figure out which side of the average our closing prices are sitting on
                2. Try to determine if we are approaching a potential reverse to the mean
                3. Select our decision on which side to enter the trade: BUY or SELL
                """
                if close_price > average_price:
                    """
                    We will take the coefficient and use conditional logic against thresholds
                    analyzed time to trigger a BUY or SELL.
                    """
                    if cv > 0.1:
                        signal = TradeSignal.BUY
                        record: TradeRecord = TradeRecord(signal,close_price,row['date'])
                        self.record_list.append(record)
                    else:
                        signal = TradeSignal.SELL
                        record: TradeRecord = TradeRecord(signal,close_price,row['date'])
                        self.record_list.append(record)   
            
                elif close_price < average_price:
                    if cv > 0.1:
                        signal = TradeSignal.SELL
                        record: TradeRecord = TradeRecord(signal,close_price,row['date'])
                        self.record_list.append(record)
                    else:
                        signal = TradeSignal.BUY
                        record: TradeRecord = TradeRecord(signal,close_price,row['date'])
                        self.record_list.append(record)   

                else:
                    signal = TradeSignal.HOLD
        return signal

    def __mean_reversion_task(self,ticker: PriceHistory,portfolio: Portfolio,type: MovingAverageType, window: float) -> TradeSignal:
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
                if(type == MovingAverageType.EXPONENTIAL):
                    stock_df = pandas.DataFrame(ticker.get_info())
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
            if(type == MovingAverageType.EXPONENTIAL):

                
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

                