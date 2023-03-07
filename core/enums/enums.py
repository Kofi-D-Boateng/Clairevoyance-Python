from enum import Enum

class MovingAverageStrategyType(Enum):
    CROSS = "CROSS"
    
class TradeType(Enum):
    BUY = "BUY"
    STRONGBUY = "STRONG BUY"
    SELL = "SELL"
    STRONG_SELL = "STRONG SELL"
    HOLD = "HOLD"

class MovingAverage(Enum):
    SIMPLE = "SIMPLE"
    EXPONENTIAL = "EXPONENTIAL"