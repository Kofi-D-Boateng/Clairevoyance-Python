from enums.enums import TradeSignal, Side
from typing import Dict, List

class TradeRecord:
    """
    The TradeRecord class is used to keep track of decisions made during the 
    execution of the strategy. We will use this class wihtin the Strategy
    class to keep a record for our back tester, where we will print out
    the record to allow for more decisions to be made.
    """
    ticker: str
    record_list: List[Dict[str,str]]
    open_position: bool

    def __init__(self, ticker: str) -> None:
        self.ticker = ticker
        self.open_position = False
        self.record_list = list()
    
    # def write(self,choice: TradeSignal, price: float, date: float) -> None:
    #     self.record_list.append((choice,price,date))
    #     print('[ACTION]: Record inserted....')

    def write_to_closed(self, value: float, date: float, side: Side) -> None:
        self.record_list.append({
                        'date':str(date),
                        'action': 'CLOSED POSITION',
                        'side': side.name,
                        'P/L': f'{value} per share',
                    })
        
    def write_to_open(self,signal: TradeSignal,side: Side, value: float,number_of_shares: float, date: float) -> None:
        a = 'BUYING '+ str(number_of_shares) + 'shares' if signal == TradeSignal.BUY else 'SELLING ' + str(number_of_shares) + 'shares'
        self.record_list.append({
                        'date':str(date),
                        'action': f'OPENED POSITION @ {str(date)} for ${value}/share. {a}',
                        'side': side.name,
                        'Price Point': value,
                    })

    

    def get_records(self) -> List[Dict[str,str]]:
        return self.record_list


class RecordHolder:
    records: Dict[str,TradeRecord]

    def __init__(self) -> None:
        self.records = dict()
    
    def insert_record(self,record: TradeRecord) -> None:
        self.records[record.ticker] = record
        print('[ACTION]: Inserted record.....')