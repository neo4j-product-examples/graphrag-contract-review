from neo4j import GraphDatabase
import json
import os



CREATE_GRAPH_STATEMENT = """
WITH $data AS data
WITH data.agreement as a

// todo proper global id for the agreement, perhaps from filename
MERGE (agreement:Agreement {contract_id: a.contract_id})
ON CREATE SET 
  agreement.name = a.agreement_name,
  agreement.effective_date = a.effective_date,
  agreement.expiration_date = a.expiration_date,
  agreement.agreement_type = a.agreement_type,
  agreement.renewal_term = a.renewal_term,
  agreement.most_favored_country = a.governing_law.most_favored_country
  //agreement.Notice_period_to_Terminate_Renewal = a.Notice_period_to_Terminate_Renewal
  

MERGE (gl_country:Country {name: a.governing_law.country})
MERGE (agreement)-[gbl:GOVERNED_BY_LAW]->(gl_country)
SET gbl.state = a.governing_law.state


FOREACH (party IN a.parties |
  // todo proper global id for the party
  MERGE (p:Organization {name: party.name})
  MERGE (p)-[ipt:IS_PARTY_TO]->(agreement)
  SET ipt.role = party.role
  MERGE (country_of_incorporation:Country {name: party.incorporation_country})
  MERGE (p)-[incorporated:INCORPORATED_IN]->(country_of_incorporation)
  SET incorporated.state = party.incorporation_state
)

WITH a, agreement, [clause IN a.clauses WHERE clause.exists = true] AS valid_clauses
FOREACH (clause IN valid_clauses |
  CREATE (cl:ContractClause {type: clause.clause_type})
  MERGE (agreement)-[clt:HAS_CLAUSE]->(cl)
  SET clt.type = clause.clause_type
  // ON CREATE SET c.excerpts = clause.excerpts
  FOREACH (excerpt IN clause.excerpts |
    MERGE (cl)-[:HAS_EXCERPT]->(e:Excerpt {text: excerpt})
  )
  //link clauses to a Clause Type label
  MERGE (clType:ClauseType{name: clause.clause_type})
  MERGE (cl)-[:HAS_TYPE]->(clType)
)"""

CREATE_VECTOR_INDEX_STATEMENT = """
CREATE VECTOR INDEX excerpt_embedding IF NOT EXISTS 
    FOR (e:Excerpt) ON (e.embedding) 
    OPTIONS {indexConfig: {`vector.dimensions`: 1536, `vector.similarity_function`:'cosine'}} 
"""

CREATE_FULL_TEXT_INDICES = [
    ("excerptTextIndex", "CREATE FULLTEXT INDEX excerptTextIndex IF NOT EXISTS FOR (e:Excerpt) ON EACH [e.text]"),
    ("agreementTypeTextIndex", "CREATE FULLTEXT INDEX agreementTypeTextIndex IF NOT EXISTS FOR (a:Agreement) ON EACH [a.agreement_type]"),
    ("clauseTypeNameTextIndex", "CREATE FULLTEXT INDEX clauseTypeNameTextIndex IF NOT EXISTS FOR (ct:ClauseType) ON EACH [ct.name]"),
    ("clauseNameTextIndex", "CREATE FULLTEXT INDEX clauseNameTextIndex IF NOT EXISTS FOR (c:ContractClause) ON EACH [c.type]"),
    ("organizationNameTextIndex", "CREATE FULLTEXT INDEX organizationNameTextIndex IF NOT EXISTS FOR (o:Organization) ON EACH [o.name]"),
    ("contractIdIndex","CREATE INDEX agreementContractId IF NOT EXISTS FOR (a:Agreement) ON (a.contract_id) ")
    
]


EMBEDDINGS_STATEMENT = """
MATCH (e:Excerpt) 
WHERE e.text is not null and e.embedding is null
SET e.embedding = genai.vector.encode(e.text, "OpenAI", { 
                    token: $token, model: "text-embedding-3-small", dimensions: 1536
                  })
"""

def index_exists(driver,  index_name):
  check_index_query = "SHOW INDEXES WHERE name = $index_name"
  result = driver.execute_query(check_index_query, {"index_name": index_name})
  return len(result.records) > 0
  

def create_full_text_indices(driver):
  with driver.session() as session:
    for index_name, create_query in CREATE_FULL_TEXT_INDICES:
      if not index_exists(driver,index_name):
        print(f"Creating index: {index_name}")
        driver.execute_query(create_query)
      else:
        print(f"Index {index_name} already exists.")        


NEO4J_URI=os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER=os.getenv('NEO4J_USERNAME', 'neo4j')
NEO4J_PASSWORD=os.getenv('NEO4J_PASSWORD')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
JSON_CONTRACT_FOLDER = './data/output/'

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))



json_contracts = [filename for filename in os.listdir(JSON_CONTRACT_FOLDER) if filename.endswith('.json')]
contract_id = 1
for json_contract in json_contracts:
  with open(JSON_CONTRACT_FOLDER + json_contract,'r') as file:
    json_string = file.read()
    json_data = json.loads(json_string)
    agreement = json_data['agreement']
    agreement['contract_id'] = contract_id
    driver.execute_query(CREATE_GRAPH_STATEMENT,  data=json_data)
    contract_id+=1
    

create_full_text_indices(driver)
driver.execute_query(CREATE_VECTOR_INDEX_STATEMENT)
print ("Generating Embeddings for Contract Excerpts...")
driver.execute_query(EMBEDDINGS_STATEMENT, token = OPENAI_API_KEY)
