

from typing import List, Optional, Annotated
from AgreementSchema import Agreement, ClauseType
from semantic_kernel.functions import kernel_function
from ContractService import  ContractSearchService


class ContractPlugin:

    def __init__(self, contract_search_service: ContractSearchService ):
        self.contract_search_service = contract_search_service
    
    @kernel_function
    async def get_contract(self, contract_id: int) -> Annotated[Agreement, "A contract"]:
        """Gets details about a contract with the given id."""
        return await self.contract_search_service.get_contract(contract_id)

    @kernel_function
    async def get_contracts(self, organization_name: str) -> Annotated[List[Agreement], "A list of contracts"]:
        """Gets basic details about all contracts where one of the parties has a name similar to the given organization name."""
        return await self.contract_search_service.get_contracts(organization_name)
    
    @kernel_function
    async def get_contracts_without_clause(self, clause_type: ClauseType) -> Annotated[List[Agreement], "A list of contracts"]:
        """Gets basic details from contracts without a clause of the given type."""
        return await self.contract_search_service.get_contracts_without_clause(clause_type=clause_type)
    
    @kernel_function
    async def get_contracts_with_clause_type(self, clause_type: ClauseType) -> Annotated[List[Agreement], "A list of contracts"]:
        """Gets basic details from contracts with a clause of the given type."""
        return await self.contract_search_service.get_contracts_with_clause_type(clause_type=clause_type)

    @kernel_function
    async def get_contracts_similar_text(self, clause_text: str) -> Annotated[List[Agreement], "A list of contracts with similar text in one of their clauses"]:
        """Gets basic details from contracts having semantically similar text in one of their clauses to the to the 'clause_text' provided."""
        return await self.contract_search_service.get_contracts_similar_text(clause_text=clause_text)
    
    @kernel_function
    async def answer_aggregation_question(self, user_question: str) -> Annotated[str, "An answer to user_question"]:
        """Answer obtained by turning user_question into a CYPHER query"""
        return await self.contract_search_service.answer_aggregation_question(user_question=user_question)
