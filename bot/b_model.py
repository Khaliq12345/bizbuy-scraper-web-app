from pydantic import BaseModel, computed_field

class Buisness(BaseModel):
    buis_id: str
    name: str
    location: str
    asking_price: float
    cash_flow: float
    gross_revenue: float
    ebitda: float
    ff_e: float
    inventory: float
    real_estate: float
    established: int
    employees: float
    reason_for_selling: str
    seller_financing_available: str
    cogs: float
    profit_margin_orig: float
    gross_margin: float
    asking_multiple: float

    @computed_field
    def profit_margin(self) -> str:
        perc = self.profit_margin_orig * 100
        return f"{round(perc, 2)}%"
    
    @computed_field
    def color(self) -> int:
        perc = self.profit_margin_orig * 100
        if perc < 11:
            return 2
        elif perc < 20:
            return 1
        else:
            return 0

    @computed_field
    def color_name(self) -> str:
        perc = self.profit_margin_orig * 100
        if perc < 11:
            return 'danger'
        elif perc < 20:
            return 'warning'
        else:
            return 'success'
    
    @computed_field
    def seller_financed_payoff_timeline(self) -> str:
        if (self.asking_price > 0) and (self.cash_flow > 0):
            seller_financed_payoff = self.asking_multiple * 12
            years = int(seller_financed_payoff // 12)
            remaining_months = round(seller_financed_payoff % 12, 2)
            return f"{years} years and {remaining_months} months"
        else:
            return "Not available"

            