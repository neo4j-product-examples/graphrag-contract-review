
from typing import TypedDict
from typing import List
from enum import Enum

# Define a Pydantic model for the Agreement schema
class Party(TypedDict):
    name: str
    role: str
    incorporation_country: str
    incorporation_state: str

class GoverningLaw(TypedDict):
    country: str
    state: str
    most_favored_country: str

class ContractClause(TypedDict):
    clause_type: str
    excerpts: List[str]

class Agreement(TypedDict):  
    agreement_name: str
    agreement_type: str
    effective_date: str
    expiration_date: str
    renewal_term: str
    notice_period_to_terminate_Renewal: str
    parties: List[Party]
    #governing_law: GoverningLaw
    clauses: List[ContractClause]


class ClauseType(Enum):
    ANTI_ASSIGNMENT = "Anti-Assignment"
    COMPETITIVE_RESTRICTION = "Competitive Restriction Exception"
    NON_COMPETE = "Non-Compete Clause"
    EXCLUSIVITY = "Exclusivity"
    NO_SOLICIT_CUSTOMERS = "No-Solicit of Customers"
    NO_SOLICIT_EMPLOYEES = "No-Solicit Of Employees"
    PRICE_RESTRICTION = "Price Restrictions"
    JOINT_IP_OWNERSHIP = "Joint IP Ownership"
    UNCAPPED_LIABILITY = "Uncapped Liability"
    MINIMUM_COMMITMENT = "Minimum Commitment"
    CAP_ON_LIABILITY = "Cap On Liability"
    NON_DISPARAGEMENT = "Non-Disparagement"
    INSURANCE = "Insurance"
    THIRD_PARTY_BENEFICIARY = "Third Party Beneficiary"
    TERMINATION_FOR_CONVENIENCE = "Termination For Convenience"
    
