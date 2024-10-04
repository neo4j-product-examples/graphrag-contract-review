import os
import asyncio
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from ContractPlugin import ContractPlugin
from ContractService import ContractSearchService
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.open_ai_prompt_execution_settings import (
    OpenAIChatPromptExecutionSettings)
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.functions.kernel_arguments import KernelArguments
import logging


logging.basicConfig(level=logging.INFO)

#get info from environment
OPENAI_KEY = os.getenv('OPENAI_API_KEY')
NEO4J_URI=os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER=os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD=os.getenv('NEO4J_PASSWORD')
service_id = "contract_search"

# Initialize the kernel
kernel = Kernel()

# Add the Contract Search plugin to the kernel
contract_search_neo4j = ContractSearchService(NEO4J_URI,NEO4J_USER,NEO4J_PASSWORD)
kernel.add_plugin(ContractPlugin(contract_search_service=contract_search_neo4j),plugin_name="contract_search")

# Add the OpenAI chat completion service to the Kernel
kernel.add_service(OpenAIChatCompletion(ai_model_id="gpt-4o",api_key=OPENAI_KEY, service_id=service_id))

# Enable automatic function calling
settings: OpenAIChatPromptExecutionSettings = kernel.get_prompt_execution_settings_from_service_id(service_id=service_id)
settings.function_choice_behavior = FunctionChoiceBehavior.Auto(filters={"included_plugins": ["contract_search"]})


# Create a history of the conversation
history = ChatHistory()

async def basic_agent() :
    userInput = None
    while True:
        # Collect user input
        userInput = input("User > ")

        # Terminate the loop if the user says "exit"
        if userInput == "exit":
            break

        # Add user input to the history
        history.add_user_message(userInput)

        # 3. Get the response from the AI with automatic function calling
        chat_completion : OpenAIChatCompletion = kernel.get_service(type=ChatCompletionClientBase)
        result = (await chat_completion.get_chat_message_contents(
            chat_history=history,
            settings=settings,
            kernel=kernel,
            arguments=KernelArguments(),
        ))[0]

        # Print the results
        print("Assistant > " + str(result))

        # Add the message from the agent to the chat history
        history.add_message(result)
    

async def test_contract_search():
    print(
        await kernel.invoke_prompt(
            function_name="get_contract",
            plugin_name="contract_search",
            prompt="Can you get me information for contract 1 and return in JSON format",
            settings=settings
        )
    )

async def test_contracts_search():
    print(
        await kernel.invoke_prompt(
            function_name="get_contracts",
            plugin_name="contract_search",
            prompt="Can you get me contracts for Mount Knowledge",
            settings=settings
        )
    )

async def test_contracts_without_clause_search():
    print(
        await kernel.invoke_prompt(
            function_name="get_contracts_without_clause",
            plugin_name="contract_search",
            prompt="Can you get me contracts without non compete clauses",
            settings=settings
        )
    )

async def test_contracts_with_clause_search():
    print(
        await kernel.invoke_prompt(
            function_name="get_contracts_with_clause_type",
            plugin_name="contract_search",
            prompt="Can you get me contracts with non compete caluse",
            settings=settings
        )
    )

if __name__ == "__main__":
    
    asyncio.run(basic_agent())

    #OR test individual data retrieval functions
    #asyncio.run(test_contract_search())
    #asyncio.run(test_contracts_search())
    #asyncio.run(test_contracts_without_clause_search())
    #asyncio.run(test_contracts_with_clause_search())


    
