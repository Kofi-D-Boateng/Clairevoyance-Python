from models.history import PriceHistory, Candle
from models.record import TradeRecord,RecordHolder
from models.portfolio import Portfolio
from enums.enums import TradeSignal, MovingAverageType, IntervalType, RewardType
from typing import Set, List, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, Future
from math import floor
import pandas




class Strategy:
    """
    The Strategy Class contains all the strategies you can use to predict to buy, sold, or hold a stock.
    """
    record_holder: RecordHolder

    def __init__(self) -> None:
        self.record_list = RecordHolder()

    ################################################################# HELPER FUNCTIONS ##################################################################################################

    ################################################################# PUBLIC FUNCTIONS ##################################################################################################

    def __generate_correct_window(self, interval_type: IntervalType, interval: int, average_window) -> int:
        if interval_type.value == IntervalType.SECOND.value:
            day_in_seconds = 1 * 24 * 60 * 60  # 86,4000sec/1day
            day_in_seconds *= average_window  # normalizing window in days to seconds in days
            average_window = day_in_seconds / interval()  # window represents number of tickers needed to be added to represent
            return average_window
        elif interval_type.value == IntervalType.MINUTE.value:
            day_in_minutes = 1 * 24 * 60
            day_in_minutes *= average_window
            average_window /= interval()
            return average_window
        elif interval_type.value == IntervalType.HOUR.value:
            day_in_hours = 24
            day_in_hours *= average_window
            day_in_hours /= interval()
        elif interval_type.value == IntervalType.DAY.value:
            average_window /= interval()
            return average_window
        elif interval_type.value == IntervalType.MONTH or interval_type.value == IntervalType.QUARTER.value or interval_type.value == IntervalType.YEAR.value:
            return 0
        else:
            print("[ERROR]: Could not determine course of action against interval type....")
            return 1

    def __generate_rsi(self,data: pandas.DataFrame ,window: int):

        delta = data['close'].diff()

        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)

        avg_gain = up.ewm(com=window-1,adjust=False).mean()
        avg_loss = down.ewm(com=window-1,adjust=False).mean()

        rs = avg_gain/avg_loss

        rsi = 100 - (100/(1+rs))

        data['rsi'] = rsi

    def __generate_moving_average(type: MovingAverageType,window: int,df: pandas.DataFrame, interval_type: IntervalType) -> None | pandas.DataFrame:
        if type == MovingAverageType.EXPONENTIAL:
            if window == 0:
                df.resample(interval_type.name).last()

            df['exponential'] = df['close'].rolling(window=window).mean()
        else:
            if window == 0:
                df.resample(interval_type.name).last()

            df['simple'] = df['close'].ewm(span=window, adjust=False).mean()

    def execute_arbitrage_strategy(self, potential_stocks: Set[PriceHistory]):
        pass

    def execute_bollinger_band_strategy(self,portfolio: Portfolio, potential_stocks: List[PriceHistory], type: MovingAverageType, window: float, std: int, rsi_window: int, rsi_upper_bound: float, rsi_lower_bound: float) -> List[Tuple[PriceHistory, TradeSignal]]:
        numOfStocks = len(potential_stocks)
        executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=numOfStocks)
        futures: List[Future[TradeSignal]] = []
        for ticker in potential_stocks:
            futures.append(executor.submit(self.__bollinger_band_task(portfolio,ticker,type,window,std,rsi_window,rsi_upper_bound,rsi_lower_bound)))
        executor.shutdown(wait=True)

        trading_results: List[Tuple[PriceHistory, TradeSignal]] = []

        for i in range(0, len(futures)):
            trading_results.append((potential_stocks[i], futures[i].result()))

        return trading_results

    def execute_dual_moving_average_strategy(self, potential_stocks: List[PriceHistory], type: MovingAverageType, first_window: int, second_window: int) -> List[Tuple[PriceHistory, TradeSignal]]:
        numOfStocks = len(potential_stocks)
        executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=numOfStocks)
        futures: List[Future[TradeSignal]] = []
        for ticker in potential_stocks:
            futures.append(executor.submit(self.__dual_moving_average_task(ticker, type, first_window, second_window)))
        executor.shutdown(wait=True)

        trading_results: List[Tuple[PriceHistory, TradeSignal]] = []

        for i in range(0, len(futures)):
            trading_results.append((potential_stocks[i], futures[i].result()))

        return trading_results

    def execute_moving_average_strategy(self, potential_stocks: List[PriceHistory], type: MovingAverageType, window: int) -> List[Tuple[PriceHistory, TradeSignal]]:
        numOfStocks = len(potential_stocks)
        executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=numOfStocks)
        futures: List[Future[TradeSignal]] = []
        for ticker in potential_stocks:
            futures.append(executor.submit(self.__moving_average_task(ticker, type, window)))
        executor.shutdown(wait=True)

        trading_results: List[Tuple[PriceHistory, TradeSignal]] = []

        for i in range(0, len(futures)):
            trading_results.append((potential_stocks[i], futures[i].result()))

        return trading_results

    def execute_pairs_trading_strategy(self, stock_pairs_list: List[Tuple[PriceHistory, PriceHistory]]) -> List[
        Tuple[Tuple[PriceHistory, PriceHistory], TradeSignal]]:
        numOfStocks = len(stock_pairs_list)
        executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=numOfStocks)
        futures: List[Future[TradeSignal]] = []
        for pair in stock_pairs_list:
            futures.append(executor.submit(self.__pairs_trading_task(pair)))
        executor.shutdown(wait=True)

        trading_results: List[Tuple[Tuple[PriceHistory, PriceHistory], TradeSignal]] = []

        for i in range(0, len(futures)):
            trading_results.append((stock_pairs_list[i], futures[i].result()))

        return trading_results

    def execute_scalping_strategy(self, potential_stocks: Set[PriceHistory]):
        pass

    def __pairs_trading_task(self, stock_pair: Tuple[PriceHistory, PriceHistory]) -> TradeSignal:
        pass

    def __bollinger_band_task(self, portfolio: Portfolio,  ticker: PriceHistory, average_type: MovingAverageType, triggers:dict, window: int = 20, std: int = 2, rsi_val: int = 14, rsi_upper_bound: float = 70.0, rsi_lower_bound: float = 30.0) -> Tuple[TradeSignal,int,float]:
        candles: List[Candle] = ticker.get_info()
        holdings = portfolio.get_holdings().get(ticker.get_ticker())
        signal: TradeSignal = TradeSignal.HOLD
        records: TradeRecord = TradeRecord(ticker=ticker.get_ticker())
        candles_df: pandas.DataFrame = pandas.DataFrame([{'open': candle.open,'close': candle.close,'low': candle.low, 'high': candle.high,'volume': candle.volume,'date': candle.date} for candle in candles])
        candles_df.reset_index(inplace=True)

        # Calculate standard deviation and the average standard deviation over the time series
        average_window = self.__generate_correct_window(ticker.get_interval_type(),ticker.get_interval(),window)
        self.__generate_moving_average(average_window,candles_df,ticker.get_interval_type())
        self.__generate_rsi(candles_df,rsi_val)
        candles_df['std'] = candles_df['close'].sub(candles_df['exponential' if average_type == MovingAverageType.EXPONENTIAL else 'simple']).rolling(window=average_window).std()
        candles_df['upper-band'] = std * candles_df['std'] + candles_df['exponential' if average_type == MovingAverageType.EXPONENTIAL else 'simple']
        candles_df['lower-band'] = (-1 * std) * candles_df['std'] + candles_df['exponential' if average_type == MovingAverageType.EXPONENTIAL else 'simple']
        
        # ACTUAL LOGIC HERE
        curr_price = candles_df['close'].iloc[-1]
        lower_band = candles_df['lower-band'].iloc[-1]
        upper_band = candles_df['upper-band'].iloc[-1]
        __rsi_val = candles_df['rsi'].iloc[-1]
        curr_date = candles_df['date'].iloc[-1]

        if upper_band > 0 and lower_band > 0:
                
                if curr_price > upper_band and __rsi_val > rsi_upper_bound and holdings.number_of_shares > 0:
                    signal = TradeSignal.SELL
                elif curr_price < lower_band and __rsi_val < rsi_lower_bound and holdings.number_of_shares > 0:
                        """
                        At this point, we do not have any shares and are in a perfect position to buy into the stock
                        We will send a buy signal and the order will be handled by the bot.
                        """
                        signal = TradeSignal.BUY
                        triggers.update('profit_trigger_amount',curr_price)
                else:
                    trigger_amount: float = holdings.purchase_amount
                    if holdings.number_of_shares > 0 and triggers.get('current_count') >= triggers.get('take_profit_count'):
                        if triggers.get('reward_type') == RewardType.DYNAMIC:
                            trigger_amount: float = triggers.get('profit_trigger_amount') + (triggers.get('profit_trigger_amount') * (triggers.get('reward_amount')/100.0))
                        else:
                            trigger_amount: float = holdings.purchase_amount + (holdings.purchase_amount * (triggers.get('reward_amount')/100.0))
                    if curr_price >= trigger_amount:
                        signal = TradeSignal.TAKE_PROFIT
                        triggers.update('profit_trigger_amount',curr_price)
             
        self.record_holder.insert_record(records)
        return (signal, curr_date)

    def __moving_average_task(self, ticker: PriceHistory, average_type: MovingAverageType, window: int) -> TradeSignal:
        # Set up variables
        signal: TradeSignal = TradeSignal.HOLD
        average_window = window
        resample = False
        candles: List[Candle] = ticker.get_info()
        data: List[dict[str, Any]] = []
        keys = {
            "exponential": f'{window}-day ema',
            "simple": f'{window}-day ma',
            'std': 'stardard-deviation',
            'z-score': f'{window}d z-score',
            'z-score roc': f'{window}d z-score roc'
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

        candles_df.reset_index(inplace=True)
        if ticker.get_interval_type().value == IntervalType.DAY.value:
            pass
        elif ticker.get_interval_type().value == IntervalType.SECOND.value:
            # day_in_seconds = 1 * 24 * 60 * 60  # 86,4000sec/1day
            # day_in_seconds *= average_window  # normalizing window in days to seconds in days
            # average_window = day_in_seconds / ticker.get_interval()  # window represents number of tickers needed to be added to represent
            pass
        elif ticker.get_interval_type().value == IntervalType.MINUTE.value:
            average_window *= floor(50*ticker.get_interval())
        elif ticker.get_interval_type().value == IntervalType.HOUR.value:
            average_window *= floor(7*ticker.get_interval())
        elif ticker.get_interval_type().value == IntervalType.MONTH or ticker.get_interval_type().value == IntervalType.QUARTER.value or ticker.get_interval_type().value == IntervalType.YEAR.value:
            resample = True
        else:
            print("[ERROR]: Could not determine course of action against interval type....")
            return TradeSignal.HOLD

        if average_type.name == MovingAverageType.EXPONENTIAL.name:
            if resample:
                candles_df = candles_df.resample(ticker.get_interval_type().name).last()

            candles_df['exponential'] = candles_df[keys['close']].rolling(window=average_window).mean()
        else:
            if resample:
                candles_df = candles_df.resample(ticker.get_interval_type().name).last()

            candles_df['simple'] = candles_df['close'].ewm(span=average_window, adjust=False).mean()

        # Calculate standard deviation and the average standard deviation over the time series
        candles_df[keys['std']] = candles_df['close'].sub(
            candles_df['exponential' if average_type.name == MovingAverageType.EXPONENTIAL.name else 'simple']).rolling(
            window=average_window).std()
        candles_df[keys['z-score']] = ((candles_df[keys['close']]- candles_df[
            'exponential' if average_type.name == MovingAverageType.EXPONENTIAL.name else 'simple']))/candles_df[keys['std']]
        candles_df[keys['z-score roc']] = ((candles_df[keys['z-score']]-candles_df[keys['z-score']].shift(1))/candles_df[keys['z-score']].shift(1))*100
        for _, row in candles_df.iterrows():
            close_price = row['close']
            average_price = row['exponential' if average_type.name == MovingAverageType.EXPONENTIAL.name else 'simple']
            zroc = row[keys['z-score roc']]

            if average_price != 0:
                """
                Once we have a average to compare against, we will follow these next steps
                1. Figure out which side of the average our closing prices are sitting on
                2. Try to determine if we are approaching a potential reverse to the mean
                3. Select our decision on which side to enter the trade: BUY or SELL
                """
                if close_price > average_price:
                    """
                    Check to see whether we have already bought or looking to shorten our position
                    """
                    if signal == TradeSignal.BUY:
                        """
                        Here are looking for opportunities to lock in profits, based on a indicator. The bot itself
                        will handle things such as STOP-LIMITS, TRAILING STOP, etc.

                        INDICATOR: We have chosen to use the rate of change of our z-score to handle profit taking areas.
                        When we receive spikes in our data above a certain threshold, we can assume that this is an area
                        where the stock is either trying to pull back or chopping sideways.
                        """
                        pass
                    else:
                        signal = TradeSignal.BUY
                        record: TradeRecord = TradeRecord(signal, close_price, row['date'])
                        self.record_list.append(record)


                # elif close_price < average_price:
                #     if cv > 0.1:
                #         signal = TradeSignal.SELL
                #         record: TradeRecord = TradeRecord(signal, close_price, row['date'])
                #         self.record_list.append(record)
                #     else:
                #         signal = TradeSignal.BUY
                #         record: TradeRecord = TradeRecord(signal, close_price, row['date'])
                #         self.record_list.append(record)

                else:
                    signal = TradeSignal.HOLD
        return signal

    def __dual_moving_average_task(self, ticker: PriceHistory, average_type: MovingAverageType, fast_window: int, slow_window: int) -> TradeSignal:
        pass