from enum import Enum

class MovingAverageStrategyType(Enum):
    CROSS = "CROSS"


class RewardType(Enum):
    NORMAL = "NORMAL"
    DYNAMIC = "DYNAMIC"
    
class TradeSignal(Enum):
    BUY = "BUY"
    STRONG_BUY = "STRONG_BUY"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"
    HOLD = "HOLD"
    LONG = "LONG"
    SHORT = "SHORT"
    TAKE_PROFIT = "TAKE_PROFIT"

class Side(Enum):
    SELL_SIDE = 0
    BUY_SIDE = 1

class MovingAverageType(Enum):
    SIMPLE = "SIMPLE"
    EXPONENTIAL = "EXPONENTIAL"

class ChartRange(Enum):
    NONE = "N"
    DAY = "D"
    MONTH = "M"
    YEAR = "Y"

class IntervalType(Enum):
    SECOND = "S"
    MINUTE = "MIN"
    HOUR = "H"
    DAY = "D"
    WEEK = "W"
    MONTH = "M"
    QUARTER = "Q"
    YEAR = "Y"

class PeriodType(Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    YTD = "ytd"