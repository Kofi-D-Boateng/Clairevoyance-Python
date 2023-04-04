from enum import Enum

class MovingAverageStrategyType(Enum):
    CROSS = "CROSS"
    
class TradeSignal(Enum):
    BUY = "BUY"
    STRONG_BUY = "STRONG BUY"
    SELL = "SELL"
    STRONG_SELL = "STRONG SELL"
    HOLD = "HOLD"
    LONG = "LONG"
    SHORT = "SHORT"

class MovingAverageType(Enum):
    SIMPLE = "SIMPLE"
    EXPONENTIAL = "EXPONENTIAL"