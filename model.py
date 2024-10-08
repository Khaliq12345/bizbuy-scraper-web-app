from sqlalchemy import  Column, Integer, Float, Text, String, CHAR
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Buisness(Base):
    __tablename__ = 'orig'
    
    buis_id = Column(String, primary_key=True, default='no id')
    name = Column(Text, default='No buiness')
    location = Column(Text, default='Not available')
    asking_price = Column(Float, default=0)
    cash_flow = Column(Float, default=0)
    gross_revenue = Column(Float, default=0)
    ebitda = Column(Float, default=0)
    ff_e = Column(Float, default=0)
    inventory = Column(Float, default=0)
    real_estate = Column(Float, default=0)
    established = Column(Integer, default=0)
    employees = Column(Integer, default=0)
    reason_for_selling = Column(Text, default='No reason')
    seller_financing_available = Column(Text, default='no')
    cogs = Column(Float, default=0)
    profit_margin_orig = Column(Float, default=0.0)
    profit_margin = Column(Text, default="0%")
    gross_margin = Column(Float, default=0.0)
    asking_multiple = Column(Float, default=0.0)
    seller_financed_payoff_timeline = Column(Text, default='Not available')
    color = Column(Integer, default=2)
    color_name = Column(Text, default='tertiary')
    buis_link = Column(Text, default='Not available')
    
class Saved(Base):
    __tablename__ = 'saved'
    
    buis_id = Column(String, primary_key=True, default='no id')
    name = Column(Text, default='No buiness')
    location = Column(Text, default='Not available')
    asking_price = Column(Float, default=0)
    cash_flow = Column(Float, default=0)
    gross_revenue = Column(Float, default=0)
    ebitda = Column(Float, default=0)
    ff_e = Column(Float, default=0)
    inventory = Column(Float, default=0)
    real_estate = Column(Float, default=0)
    established = Column(Integer, default=0)
    employees = Column(Integer, default=0)
    reason_for_selling = Column(Text, default='No reason')
    seller_financing_available = Column(Text, default='no')
    cogs = Column(Float, default=0)
    profit_margin_orig = Column(Float, default=0.0)
    profit_margin = Column(Text, default="0%")
    gross_margin = Column(Float, default=0.0)
    asking_multiple = Column(Float, default=0.0)
    seller_financed_payoff_timeline = Column(Text, default='Not available')
    color = Column(Integer, default=2)
    color_name = Column(Text, default='tertiary')
    buis_link = Column(Text, default='Not available')
