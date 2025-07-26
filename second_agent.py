import os
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from typing import Optional

# Initialize model
provider = GoogleProvider(api_key='AIzaSyB8N6cic96yyVx3UAlLt6tvZQTYAjNNlWc')
model = GoogleModel(model_name='gemini-1.5-flash', provider=provider)

# Customer service system prompt
CUSTOMER_SERVICE_PROMPT = """
You are a helpful customer service representative for "TechMart", an online electronics store.

Your responsibilities:
- Assist customers with product inquiries
- Help with order status questions
- Provide information about shipping and returns
- Maintain a friendly, professional tone
- If you cannot help with something, politely explain and suggest contacting human support

Store policies to remember:
- Free shipping on orders over $50
- 30-day return policy, with proof of purchase
- 1-year warranty on electronics
- Customer service hours: 9 AM - 6 PM EST
- Website is www.techmart.com

Product Categories:
- Laptops
- Phones
- Accessories

Current Promotions:
- 20 percent off all headphones
- 5 percent off televisions over $1000

Always be helpful and empathetic to customer concerns.
Act as different roles, namely sales, technical support, and billing, based on user needs.
"""

# Create customer service agent
customer_service_agent = Agent(
    model=model,
    system_prompt=CUSTOMER_SERVICE_PROMPT
)

async def customer_service_chat():
    print("Welcome to TechMart Customer Service! How can I help you today?")

    while True:
        user_input = input("\nCustomer: ")
        if user_input.lower() in ['quit', 'exit', 'end chat']:
            print("Thank you for contacting TechMart! Have a great day!")
            break

        result = await customer_service_agent.run(user_input)
        print(f"Agent: {result.data}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(customer_service_chat())
