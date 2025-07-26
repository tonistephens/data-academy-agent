from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Dict

class RefundRequest(BaseModel):
    order_id: str
    reason: str
    amount: float
    status: str = "pending"

REFUNDS_DB = {}