from models.history import PriceHistory, Candle
from models.record import TradeRecord,RecordHolder
from models.portfolio import Portfolio
from enums.enums import TradeSignal, MovingAverageType, IntervalType, RewardType
from typing import Set, List, Tuple
from concurrent.futures import ThreadPoolExecutor, Future
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

    def __generate_moving_average(self,type: MovingAverageType,window: int,df: pandas.DataFrame, interval_type: IntervalType) -> None:
        if type == MovingAverageType.EXPONENTIAL:
            if window == 0:
                df.resample(interval_type.name).last()

            df[f'{window}'] = df['close'].rolling(window=window).mean()
        else:
            if window == 0:
                df.resample(interval_type.name).last()

            df[f'{window}'] = df['close'].ewm(span=window, adjust=False).mean()

    def execute_arbitrage_strategy(self, potential_stocks: Set[PriceHistory]):
        pass

    def execute_bollinger_band_strategy(self,portfolio: Portfolio, potential_stocks: List[PriceHistory], triggers:dict, type: MovingAverageType, window: float, std: int, rsi_window: int, rsi_upper_bound: float, rsi_lower_bound: float) -> List[Tuple[PriceHistory, TradeSignal]]:
        numOfStocks = len(potential_stocks)
        executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=numOfStocks)
        futures: List[Future[Tuple[TradeSignal,int]]] = []
        for ticker in potential_stocks:
            futures.append(executor.submit(self.__bollinger_band_task(portfolio,ticker,type,triggers,window,std,rsi_window,rsi_upper_bound,rsi_lower_bound)))
        executor.shutdown(wait=True)

        trading_results: List[Tuple[PriceHistory, TradeSignal,int]] = []

        for i in range(0, len(futures)):
            result,date = futures[i].result()
            trading_results.append((potential_stocks[i],result,date))

        return trading_results

    def execute_moving_average_strategy(self, potential_stocks: List[PriceHistory], type: MovingAverageType, first_window: int, second_window: int) -> List[Tuple[PriceHistory, TradeSignal]]:
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
        self.__generate_moving_average(average_type,average_window,candles_df,ticker.get_interval_type())
        self.__generate_rsi(candles_df,rsi_val)
        candles_df['std'] = candles_df['close'].sub(candles_df[f'{window}']).rolling(window=average_window).std()
        candles_df['upper-band'] = std * candles_df['std'] + candles_df[f'{window}']
        candles_df['lower-band'] = (-1 * std) * candles_df['std'] + candles_df[f'{window}']
        
        # ACTUAL LOGIC HERE
        curr_price = candles_df['close'].iloc[-1]
        lower_band = candles_df['lower-band'].iloc[-1]
        upper_band = candles_df['upper-band'].iloc[-1]
        __rsi_val = candles_df['rsi'].iloc[-1]
        curr_date = candles_df['date'].iloc[-1]

        if upper_band > 0 and lower_band > 0:
                
                if curr_price > upper_band and __rsi_val > rsi_upper_bound and holdings.number_of_shares > 0:
                    signal = TradeSignal.SELL
                    triggers.update('current_count',0)
                elif curr_price < lower_band and __rsi_val < rsi_lower_bound and holdings.number_of_shares > 0:
                        """
                        At this point, we do not have any shares and are in a perfect position to buy into the stock
                        We will send a buy signal and the order will be handled by the bot.
                        """
                        signal = TradeSignal.BUY
                        triggers.update('profit_trigger_amount',curr_price)
                else:
                    trigger_amount: float = holdings.purchase_amount
                    if holdings.number_of_shares > 0 and triggers.get('current_count') >= triggers.get('count_limit'):
                        if triggers.get('reward_type') == RewardType.DYNAMIC:
                            trigger_amount: float = triggers.get('profit_trigger_amount') + (triggers.get('profit_trigger_amount') * (triggers.get('reward_amount')/100.0))
                        else:
                            trigger_amount: float = holdings.purchase_amount + (holdings.purchase_amount * (triggers.get('reward_amount')/100.0))
                    if curr_price >= trigger_amount:
                        signal = TradeSignal.TAKE_PROFIT
                        triggers.update('profit_trigger_amount',curr_price)
             
        self.record_holder.insert_record(records)
        return (signal, curr_date)

    def __dual_moving_average_task(self,portfolio: Portfolio, ticker: PriceHistory, average_type: MovingAverageType, fast_window: int, slow_window: int,triggers:dict,rsi_val: int = 14,rsi_upper_bound: float = 70.0, rsi_lower_bound: float = 30.0) -> TradeSignal:
        candles: List[Candle] = ticker.get_info()
        holdings = portfolio.get_holdings().get(ticker.get_ticker())
        signal: TradeSignal = TradeSignal.HOLD
        records: TradeRecord = TradeRecord(ticker=ticker.get_ticker())
        candles_df: pandas.DataFrame = pandas.DataFrame([{'open': candle.open,'close': candle.close,'low': candle.low, 'high': candle.high,'volume': candle.volume,'date': candle.date} for candle in candles])
        candles_df.reset_index(inplace=True)


        f_window = self.__generate_correct_window(ticker.get_interval_type(),ticker.get_interval(),fast_window)
        s_window = self.__generate_correct_window(ticker.get_interval_type(),ticker.get_interval(),slow_window)

        self.__generate_moving_average(average_type,f_window,candles_df,candles_df,ticker.get_interval_type())
        self.__generate_moving_average(average_type,s_window,candles_df,candles_df,ticker.get_interval_type())
        self.__generate_rsi(candles_df,rsi_val)


        curr_price = candles_df['close'].iloc[-1]
        curr_date = candles_df['date'].iloc[-1]
        __rsi_val = candles_df['rsi'].iloc[-1]
        fast_avg_price = candles_df[f'{f_window}']
        slow_avg_price = candles_df[f'{s_window}']

        if fast_avg_price > 0.0 and slow_avg_price > 0.0:
            if curr_price > slow_avg_price and curr_price > fast_avg_price and __rsi_val > rsi_upper_bound:
                signal = TradeSignal.SELL
                triggers.update('current_count',0)
            elif curr_price < slow_avg_price and curr_price < fast_avg_price and __rsi_val < rsi_lower_bound:
                signal = TradeSignal.BUY
                triggers.update('profit_trigger_amount',curr_price)
            else:
                trigger_amount: float = holdings.purchase_amount
                if holdings.number_of_shares > 0 and triggers.get('current_count') >= triggers.get('count_limit'):
                    if triggers.get('reward_type') == RewardType.DYNAMIC:
                        trigger_amount: float = triggers.get('profit_trigger_amount') + (triggers.get('profit_trigger_amount') * (triggers.get('reward_amount')/100.0))
                    else:
                        trigger_amount: float = holdings.purchase_amount + (holdings.purchase_amount * (triggers.get('reward_amount')/100.0))
                    if curr_price >= trigger_amount:
                        signal = TradeSignal.TAKE_PROFIT
                        triggers.update('profit_trigger_amount',curr_price)
        
        self.record_holder.insert_record(records)
        return (signal, curr_date)
    
