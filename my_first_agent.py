import os
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings

# Initialize the model
provider = GoogleProvider(api_key='AIzaSyB8N6cic96yyVx3UAlLt6tvZQTYAjNNlWc')
model = GoogleModel(model_name='gemini-1.5-flash', provider=provider)

# Create a basic agent
agent = Agent(model=model)

# Simple conversation function
async def chat():
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit']:
            break

        result = await agent.run(user_input)
        print(f"Agent: {result.data}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(chat())