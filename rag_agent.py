import os
import json
import re
from typing import List, Dict, Any, Optional
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel
from sample_products import PRODUCT_DATA
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from thefuzz import fuzz

def normalize_text(text: str) -> str:
        """Lowercase and remove punctuation"""
        return re.sub(r"[^\w\s]", "", text.lower())

SET_TOKEN = 80

class ProductKnowledgeBase:
    def __init__(self, products: List[Dict]):
        self.products = products

    def search_products(self, query: str, category: str = None) -> List[Dict]:
        """Simple keyword-based product search"""
        query_keywords = normalize_text(query)
        results = []

        for product in self.products:
            searchable_text = normalize_text(
                product['name'] + ' ' +
                product['description'] + ' ' +
                ' '.join(product['features']) 
            )

            score = fuzz.token_set_ratio(query_keywords, searchable_text)
            if score >= SET_TOKEN:
                if category is None or product['category'].lower() == category.lower():
                    results.append((score, product))           

        results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in results[:5]]
        # return results[:5]

    def get_product_by_id(self, product_id: str) -> Dict:
        """Get specific product by ID"""
        for product in self.products:
            if product['id'] == product_id:
                return product
        return None

# Initialize knowledge base
kb = ProductKnowledgeBase(PRODUCT_DATA)

# Enhanced system prompt with RAG context
RAG_SYSTEM_PROMPT = """
You are a knowledgeable customer service representative for TechMart electronics store.

When customers ask about products, you will be provided with relevant product information from our database.
Use this information to give accurate, helpful responses about:
- Product specifications and features
- Pricing and availability
- Comparisons between products
- Recommendations based on customer needs

Always base your product information on the provided data. If you don't have information about a specific product, let the customer know and offer to help them find similar items.

Store policies:
- Free shipping on orders over $50
- 30-day return policy
- Warranty varies by product (check product details)
- Customer service hours: 9 AM - 6 PM EST
"""

# Create RAG-enabled agent
def get_product_context(user_message: str) -> str:
    """Retrieve relevant product information based on user query"""
    # Simple keyword extraction for product search
    search_results = kb.search_products(user_message)

    if not search_results:
        return "No specific product information found for this query."

    context = "Relevant products from our database:\n\n"
    for product in search_results:
        context += f"**{product['name']}** (ID: {product['id']})\n"
        context += f"Price: ${product['price']}\n"
        context += f"Category: {product['category']}\n"
        context += f"Description: {product['description']}\n"
        context += f"Key Features: {', '.join(product['features'])}\n"
        context += f"Warranty: {product['warranty']}\n"
        context += f"In Stock: {'Yes' if product['in_stock'] else 'No'}\n\n"
    return context

provider = GoogleProvider(api_key='AIzaSyB8N6cic96yyVx3UAlLt6tvZQTYAjNNlWc')
model = GoogleModel('gemini-2.5-flash', provider=provider)

rag_agent = Agent(
    model=model,
    system_prompt=RAG_SYSTEM_PROMPT
)

async def rag_customer_service():
    print("Welcome to TechMart Customer Service with Product Knowledge! How can I help you?")

    while True:
        user_input = input("\nCustomer: ")
        if user_input.lower() in ['quit', 'exit', 'end chat']:
            print("Thank you for contacting TechMart! Have a great day!")
            break

        # Get relevant product context
        product_context = get_product_context(user_input)

        # Combine user query with context
        enhanced_prompt = f"Customer Query: {user_input}\n\nProduct Information:\n{product_context}"

        result = await rag_agent.run(enhanced_prompt)
        print(f"Agent: {result.data}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(rag_customer_service())
