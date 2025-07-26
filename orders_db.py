from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Dict

class Order(BaseModel):
    order_id: str
    customer_email: str
    products: List[Dict]
    total_amount: float
    status: str
    order_date: datetime
    shipping_address: str

ORDERS = {
    "ORD-001": Order(
        order_id="ORD-001",
        customer_email="john@example.com",
        products=[{"name": "TechMart Pro Laptop", "price": 899.99, "quantity": 1}],
        total_amount=899.99,
        status="delivered",
        order_date=datetime.now() - timedelta(days=5),
        shipping_address="123 Main St, Anytown, USA"
    ),
    "ORD-002": Order(
        order_id="ORD-002",
        customer_email="jane@example.com",
        products=[{"name": "SmartPhone X Pro", "price": 799.99, "quantity": 1}],
        total_amount=799.99,
        status="shipped",
        order_date=datetime.now() - timedelta(days=2),
        shipping_address="456 Oak Ave, Somewhere, USA"
    )
}