

# Historical Price data for a given stock
class PriceHistory:
    # The stock symbol assigned to this list of data
    ticker:str
    # The historical price data on the stock returned
    # from the api. Includes the open,close,high,low,
    # datetime, and volume trade at that specific moment
    info:list
    
    def __init__(self,ticker:str,info:list):
        self.ticker = ticker
        self.info = info

    def get_ticker(self) -> str:
        return self.ticker

    def get_info(self) -> list:
        return self.info    


# Portfolio class that will hold info regarding the traders
# current account's funds and holding
class Portfolio:
    current_available_funds:float
    total_funds:float
    holdings:dict

    def __init__(self,current_funds:float,total_funds:float,holdings:dict):
        self.current_available_funds = current_funds
        self.total_funds = total_funds
        self.holdings = holdings

    def get_current_funds(self) -> float:
        return self.current_available_funds

    def get_total_funds(self) -> float:
        return self.total_funds     

    def get_holdings(self) -> dict:
        return self.holdings         