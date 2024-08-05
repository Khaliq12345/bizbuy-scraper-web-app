from nicegui import ui

ui.add_head_html(
    """<meta name="viewport" content="width=device-width, initial-scale=1.0">"""
)

excludes = [
    "Reason for selling",
    "Seller Financing Available",
    "Seller Financed Payoff Timeline",
    "Employees",
    "Established",
    "Profit Margin",
    "Location",
]

mappers = [
    {"name": "State", 'field': 'location'},
    {"name": "Asking Price", 'field': 'asking_price'},
    {"name": "Cash Flow", 'field': 'cash_flow'},
    {"name": "Gross Revenue", 'field': 'gross_revenue'},
    {"name": "Profit Margin", 'field': 'profit_margin'},
    {"name": "Asking Multiple", "field": 'asking_multiple'},
    {"name": "Gross Margin", "field": 'gross_margin'},
    {"name": "COGS", 'field': "cogs"},
    {"name": "EBITDA", 'field': "ebitda"},
    {"name": "Inventory", 'field': "inventory"},
    {"name": "Real Estate", "field": "real_estate"},
    {"name": "Established", "field": 'established'},
    {"name": "Employees", "field": "employees"},
    {"name": "Seller Financed Payoff Timeline", "field": "seller_financed_payoff_timeline"},
    {"name": "Seller Financing Available", 'field': 'seller_financing_available'},
    {"name": "Reason for selling", 'field': "reason_for_selling"},
]
 
filters_mappers = [
    {"name": "Asking price", "field": "asking_price", 'type': "number"},
    {"name": "Cash Flow", "field": "cash_flow", 'type': "number"},
    {"name": "Asking Multiple", "field": "asking_multiple", 'type': "number"},
    {"name": "Order by profit margin", "field": "profit_margin", 'type': "toggle"},
    {"name": "Order by cash flow", "field": "cash_flow", 'type': "toggle"},
]