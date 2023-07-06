from typing import List
from datetime import datetime
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
    period: int
    """
    The period that the chart spans. The range should
    be used only when the chart is within one of the
    specified ranges. If using a chart between
    unique timestamps, passing a PeriodType is also not
    needed. 
    
    Default set to DAY
    """
    period_type: PeriodType
    
    frequency_type: FrequencyType

    frequency: int

    start_date: int
    """
    The beginning date of the time series in epoch milliseonds
    """
    end_date: int
    """
    The ending date of the time series in epoch milliseonds
    """

    def __init__(self,ticker: str,info: List[Candle], start_date: datetime = None, end_date: datetime = None, frequency_type: FrequencyType = FrequencyType.DAY, frequency: int = 0  , period: int = 0, period_type: PeriodType = PeriodType.DAY):
        self.ticker = ticker
        self.frequency_type = frequency_type
        self.interval = frequency
        self.period = period
        self.period_type = period_type
        self.candles = info
        self.start_date = self.date_to_epoch(start_date) if start_date is not None else None
        self.end_date = self.date_to_epoch(end_date) if start_date is not None else None

    @staticmethod
    def date_to_epoch(date_string: datetime):
        dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S.%f")
        return int((dt - datetime(1970, 1, 1)).total_seconds() * 1000)

    def get_ticker(self) -> str: return self.ticker

    def get_info(self) -> List[Candle]: return self.candles    
    
    def get_period(self) -> int: return self.period
    
    def get_period_type(self) -> PeriodType: return self.period_type
    
    def get_frequency(self) -> int: return self.frequency
    
    def get_frequency_type(self) -> FrequencyType: return self.frequency_type

    def get_start_date(self) -> int: return self.start_date

    def get_end_date(self) -> int: return self.end_date
