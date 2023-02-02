from models.models import PriceHistory


# A Class created to make informed decisions on the market
# and the assets and securities traded on those markets.
# You can set your arbitrage threshold and correlation
# threshold when creating the close or go with the default
# values embedded in the class.
class MarketAnalyzer:
    types = {"sma","ema"}
    arbitrage_threshold:float
    correlation_threshold:float

    def __init__(self,arb_thresh:float,corr_thresh:float):
        self.arbitrage_threshold = arb_thresh
        self.correlation_threshold = corr_thresh

  #--------------------------------------------------------------------------------- GETTERS AND SETTERS ---------------------------------------------------------------------------------------

    def get_arbitrage_threshold(self) -> float:
        return self.arbitrage_threshold

    def get_correlation_threshold(self) -> float:
        return self.arbitrage_threshold    

    def set_arbitrage_threshold(self, threshold:float) -> None:
        self.arbitrage_threshold = threshold

    def set_correlation_threshold(self, threshold:float) -> None:
        self.correlation_threshold = threshold

  #--------------------------------------------------------------------------------- REGULAR METHODS -------------------------------------------------------------------------------------------

    # Takes in a stock and window and returns the moving average based on
    # the window.
    def generate_sma(self,stock:PriceHistory, window:float) -> list:

        sma = list()
        candles = stock.get_info()
        start,end,endOfCandles = 0,1,len(candles -1)

        while end <= endOfCandles:
            counter,currSum, = 0,candles[start]["close"]

            while counter <= window:
                currSum += candles[end]["close"]
                counter+1
                end+1

            dateAvgPair = (candles[end]["datetime"],(currSum/window))
            start+1
            end = start + 1
            counter = 0

            sma.append(dateAvgPair)

        return sma

    # Takes in two tickers and will return a boolean whether there
    # is a correlation between the two tickers based off of Kendall's
    # Tau. Types of correlation to try are but not limited to: 
    #   positive(pos): both stocks are trending in the positive direction, 
    #   negative(neg): both stocks are trending in the negative direction, 
    def generate_correlation(self,stock1:PriceHistory, stock2:PriceHistory) -> float:
        # WE NEED TO SEE IF THERE IS A CORRELATION ON THE CLOSE, BUT IT
        # NEEDS TO BE AN ADJUSTED PRICE CLOSE.
        import pandas as pd
        from scipy.stats import kendalltau

        stock_1,stock_2 = pd.DataFrame(stock1.get_info()),pd.DataFrame(stock2.get_info())

        correlation,_ = kendalltau(stock_1,stock_2)

        return correlation

    # Takes in a dictionary which should a PriceHistory class object as the key
    #  and the values should be a list of PriceHistory class object that you want
    # to be checked for correlation. The function returns a dictionary of a stock
    # and its correlation coefficient to the other stocks. 
    def generate_correlation_dict(self,stocks:dict) -> dict:
        finshedCorrDict:dict = dict()
        for stock in stocks:
            # Grab the list of stocks waiting to be processed
            stockList:list = stocks[stock]
            # iterate through this list of stocks and perform
            # correlation tasks
            for queuedStock in stockList:
                correlation = self.generate_correlation(stock.get_info(),queuedStock.get_info())

                if stock in finshedCorrDict:
                    finshedCorrDict.get(stock).append((queuedStock,correlation))
                else:
                    newList:list = list()
                    newList.append((queuedStock,correlation))
                    finshedCorrDict.setdefault(stock,newList)
        return finshedCorrDict

    def generate_diverging_sentiment(self,stock1:PriceHistory, stock2:PriceHistory) -> bool:
        import pandas as pd

        stock_1, stock_2 = pd.DataFrame(stock1.get_info()),pd.DataFrame(stock2.get_info())

        difference = stock_1["Close"] - stock_2["Close"]

        if all(difference[i] < difference[i+1] for i in range(len(difference)-1)):
            return True
        elif all(difference[i] > difference[i+1] for i in range(len(difference)-1)):
            return False    

    def generate_diverging_dict(self,stocks:dict) -> dict:
        
        returningDict:dict = dict()

        for stock in stocks:
            stockList:list = stocks[stock]

            for curr in stockList:
                result:bool = self.generate_diverging_sentiment(stock,curr)
                if stock in returningDict:
                    returningDict[stock].append((curr,result))
                else:
                    newList:list = list()
                    newList.append((curr,result))
                    returningDict[stock] = newList
        return returningDict    

    def generate_ema(self,stock:PriceHistory,window:float) -> list:
        ema:list = list()
        candles:list = stock.get_info()
        start,end,eoc = 0,1,len(candles-1)
        alpha:float = 2.0/(window+1.0)

        while end <= eoc:
            counter:int = 0
            currEma:float = candles[start]["close"]

            while counter <= window:
                currEma = (candles[start]["close"] * alpha) + (currEma * (1-alpha))
               
                end+1
                counter+1

            dateAvgPair = (candles[end]["datetime"],(currEma/window))
            start+1
            end = end + 1
            counter = 0
            ema.append(dateAvgPair)

        return ema            

    def generate_moving_average(self,stock:PriceHistory, window:int, type:str)-> list:
        
        if type == "sma":
            return self.generate_sma(stock,window)
        elif type == "ema":
            return self.generate_ema(stock,window)    
        
    # Takes in a single stock or a vector of stocks and window or
    # vector of windows and returns an unorder map with the key
    # being a stock and the value being a ordered map with the
    # key being a window and the values being a vector of either
    # a simple moving average or exponential moving average.
    def generate_moving_average_dict(self,stocks, windows, type:str) -> dict:
        if type not in self.types:
            # THROW EXCEPTION
            pass

        ma_dict,inner_map = {},{}

        # Check for double lists
        # Check for single list & single entity
        if isinstance(stocks,list):
            if isinstance(windows,list):
                for stock in stocks:
                    for window in windows:
                        ma_list = self.generate_moving_average(stock=stock,window=window,type=type)
                        inner_map[window] = ma_list
                        
                        ma_dict[stock] = inner_map
                return ma_dict     
            else:
                for stock in stocks:
                    ma_list = self.generate_moving_average(stock=stock,window=window,type=type)
                    inner_map[window] = ma_list
                    ma_dict[stock] = inner_map
                
                return ma_dict
        
        else:
            if isinstance(windows,list):
                for window in windows:
                    ma_list = self.generate_moving_average(stock=stock,window=window,type=type)
                    inner_map[window] = ma_list
                    ma_dict[stock] = inner_map
                
                return ma_dict

            else:
                ma_list = self.generate_moving_average(stock=stock,window=window,type=type)
                inner_map[window] = ma_list
                ma_dict[stock] = inner_map

                return ma_dict   

    # Takes in a ticker, a market, a start date, and end date to detect where the underlying trend
    # is in the stock. It will return a char of '+' or '-' indicating which direction the trend is
    # going.
    def generate_stock_trend(self,stock:PriceHistory, short_term_window:float,long_term_window:float) -> str:
        
        short_term_ema, long_term_sma, = self.generate_sma(stock=stock,window=short_term_window),self.generate_sma(stock=stock,window=long_term_window)

        lt_pct_change:float = ((long_term_sma[-1]["close"] - long_term_sma[0]["close"])/long_term_sma[0]["close"])*100.00
        st_pct_change:float = ((short_term_ema[-1]["close"] - short_term_ema[0]["close"])/short_term_ema[0]["close"])*100.00
        
        long_term:str = ""
        short_term:str = ""

        if lt_pct_change < 0:
            long_term = f'The long term trend for {stock.get_ticker()} is downward with a percent change of {lt_pct_change}'
        else:
            long_term = f'The long term trend for {stock.get_ticker()} is upward with a percent change of {lt_pct_change}'

        if st_pct_change < 0:
            short_term = f'The long term trend for {stock.get_ticker()} is downward with a percent change of {st_pct_change}'
        else:
            short_term = f'The long term trend for {stock.get_ticker()} is upward with a percent change of {st_pct_change}'

        return f'{long_term}. {short_term}.'

    # Takes in a ticker set, a market set, a start date, and end date to detect where the underlying trend
    # is in the stock. It will return a dictionary where the key will be a ticker and the value will be a 
    # another dictionary with the market being the key and the value a char of either '+' or '-' indicating
    # which direction the stock is trending on the given exchange.
    def generate_stock_trend_dict(self,stocks:list,short_term_window:float,long_term_window:float) -> dict:
        trend_dict:dict = {}

        for stock in stocks:
            sentiment:str = self.generate_stock_trend(stock,short_term_window,long_term_window)
            trend_dict[stock] = sentiment

        return trend_dict