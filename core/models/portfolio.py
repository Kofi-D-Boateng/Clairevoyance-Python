from typing import Dict


class Holdings:
    number_of_shares: float
    purchase_amount: float
    value: float

    def __init__(self,nos: float, pps: float, val: float) -> None:
        self.number_of_shares = nos
        self.purchase_amount = pps
        self.value = val
        



class Portfolio:
    """
    Portfolio class that will hold info regarding the traders current account's funds and holding
    """
    current_available_funds:float
    total_funds:float
    holdings: Dict[str,Holdings]
    max_exposure_allowed:float
    stop_loss:float
    limit_order:float

    def __init__(self,current_funds:float,total_funds:float,holdings:Dict[str,Holdings],max_exposure_allowed:float,stop_loss_percent:float,limit_order_percent):
        self.current_available_funds = current_funds
        self.total_funds = total_funds
        self.holdings = holdings
        self.max_exposure_allowed
        self.stop_loss = 1 - stop_loss_percent
        self.limit_order = 1 + limit_order_percent

    def get_current_funds(self) -> float:
        return self.current_available_funds

    def get_total_funds(self) -> float:
        return self.total_funds     

    def get_holdings(self) -> Dict[str,Holdings]:
        return self.holdings       

    def get_max_exposure_allowed(self) -> float:
        return self.max_exposure_allowed      

    def get_stop_loss(self)-> float:
        return self.stop_loss

    def get_limit_order(self) -> float:
        return self.limit_order    
