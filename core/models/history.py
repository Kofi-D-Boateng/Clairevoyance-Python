from typing import List
from enums.enums import *

class Candle:
    """
    A class that mimics a candle and the values that come with it
    """
    open: float
    close: float
    low: float
    high: float
    volume: float
    date: int

    def __init__(self,open: float,close: float,low: float,high: float,volume: float,date: int):
        self.open = open
        self.close = close
        self.low = low
        self.high = high
        self.volume = volume
        self.date = date

class PriceHistory:
    """
    Historical Price data for a given stock
    """
    ticker: str
    """
    The stock symbol assigned to this list of data
    """
    candles: List[Candle]
    """
    The historical price data on the stock returned
    from the api. Includes the open,close,high,low,
    datetime, and volume trade at that specific moment
    """
    range: ChartRange
    """
    The range that the chart spans. The range should
    be used only when the chart is within one of the
    specified ranges. If using a chart between
    unique timestamps, passing a ChartRange is not
    needed. 
    
    Default set to NONE
    """
    range_interval: int
    """
    The interval for which the range of the chart spans.

    For example, a 3 Month chart will have a range set
    to ChartRange.MONTH and a range_interval of 3. This
    is important to be able to correctly calculate 
    statisical points for the stock.
    """
    interval_type: IntervalType

    interval: int

    def __init__(self,ticker: str,info: List[Candle], interval_type: IntervalType, interval: float  ,range_interval: float = 0, range: ChartRange = ChartRange.NONE):
        self.ticker = ticker
        self.candles = info

    def get_ticker(self) -> str:
        return self.ticker

    def get_info(self) -> List[Candle]:
        return self.candles    
    
    def get_range(self) -> ChartRange:
        return self.range
    
    def get_range_interval(self) -> int:
        return self.range_interval
    
    def get_interval_type(self) -> IntervalType:
        return self.interval_type
    
    def get_interval(self) -> int:
        return self.interval
