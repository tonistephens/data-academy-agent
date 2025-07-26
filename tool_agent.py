import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from sample_products import PRODUCT_DATA
from orders_db import ORDERS, Order
from refunds import REFUNDS_DB, RefundRequest

# Tool functions
def check_order_status(order_id: str) -> Dict:
    """Check the status of a customer order"""
    if order_id in ORDERS:
        order = ORDERS[order_id]
        return {
            "found": True,
            "order_id": order.order_id,
            "status": order.status,
            "order_date": order.order_date.strftime("%Y-%m-%d"),
            "total_amount": order.total_amount,
            "products": order.products
        }
    return {"found": False, "message": "Order not found"}

def process_refund(order_id: str, reason: str, customer_email: str) -> Dict:
    """Process a refund request for an order"""   
    if order_id not in ORDERS:
        return {"found": False, "message": "Order not found"}
    
    order = ORDERS[order_id]

    # Verify customer email matches
    if order.customer_email.lower() != customer_email.lower():
        return {"success": False, "message": "Email does not match order records"}

    # Check if order is eligible for refund
    if order.status not in ["delivered", "shipped"]:
        return {"success": False, "message": "Order not eligible for refund"}

    # Create refund request
    refund_id = f"REF-{len(REFUNDS_DB) + 1:03d}"
    refund = RefundRequest(
        order_id=order_id,
        reason=reason,
        amount=order.total_amount
    )

    REFUNDS_DB[refund_id] = refund

    return {
        "success": True,
        "refund_id": refund_id,
        "amount": order.total_amount,
        "message": "Refund request submitted successfully. You will receive confirmation within 2-3 business days."
    }

def update_shipping_address(order_id: str, new_address: str, customer_email: str) -> Dict:
    """Update shipping address for an order"""
    if order_id not in ORDERS:
        return {"success": False, "message": "Order not found"}

    order = ORDERS[order_id]

    # Verify customer email
    if order.customer_email.lower() != customer_email.lower():
        return {"success": False, "message": "Email does not match order records"}

    # Check if order can be modified
    if order.status in ["delivered", "cancelled"]:
        return {"success": False, "message": "Cannot modify address for delivered or cancelled orders"}

    # Update address
    ORDERS[order_id].shipping_address = new_address

    return {
        "success": True,
        "message": f"Shipping address updated successfully for order {order_id}",
        "new_address": new_address
    }

def get_refund_status(refund_id: str) -> Dict:
    """Check the status of a refund request"""
    if refund_id in REFUNDS_DB:
        refund = REFUNDS_DB[refund_id]
        return {
            "found": True,
            "refund_id": refund_id,
            "order_id": refund.order_id,
            "status": refund.status,
            "amount": refund.amount,
            "reason": refund.reason
        }
    return {"found": False, "message": "Refund request not found"}

def check_product_availability(order_id: str) -> Dict:
    """Check if product in stock"""
    if order_id in PRODUCT_DATA:
        product = PRODUCT_DATA[order_id]
        return {
            "found": True,
            "id": order_id,
            "name": product.name,
            "price": product.price,
            "in_stock": product.in_stock
        }
    return {"found": False, "message": "Order not found"}

# Enhanced system prompt for tool calling
TOOL_SYSTEM_PROMPT = """
You are an advanced customer service agent for TechMart with access to order management tools.

You can help customers with:
- Checking order status
- Processing refund requests
- Updating shipping addresses
- Checking refund status
- Checking product availability

When customers request these actions, use the appropriate tools to help them. Always ask for necessary information like order ID and email address for verification.

For refund requests, be empathetic and gather the reason for the refund to improve our services.

Store policies:
- 30-day return policy for most items
- Free shipping on orders over $50
- Refunds processed within 3-5 business days
- Address changes only possible before shipping
"""

# Create agent with tools
provider = GoogleProvider(api_key='AIzaSyB8N6cic96yyVx3UAlLt6tvZQTYAjNNlWc')
model = GoogleModel('gemini-2.5-flash', provider=provider)

tool_agent = Agent(
    model=model,
    system_prompt=TOOL_SYSTEM_PROMPT,
    tools=[
        check_order_status,
        process_refund,
        update_shipping_address,
        get_refund_status,
        check_product_availability
    ]
)

async def tool_customer_service():
    print("Welcome to TechMart Advanced Customer Service! I can help you with orders, refunds, and more.")
    print("Available services: Check order status, process refunds, update addresses, check refund status, check product availability")

    while True:
        user_input = input("\nCustomer: ")
        if user_input.lower() in ['quit', 'exit', 'end chat']:
            print("Thank you for contacting TechMart! Have a great day!")
            break

        result = await tool_agent.run(user_input)
        print(f"Agent: {result.data}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(tool_customer_service())
