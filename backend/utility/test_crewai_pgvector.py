#from crewai_tools import PGSearchTool
import os
from dotenv import load_dotenv
import urllib.parse
from sqlalchemy import create_engine
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.documents import Document
import psycopg2 

from crewai import Agent, Task, Crew, Process, LLM
from textwrap import dedent

load_dotenv()

db_host = os.getenv('DB_HOST')
db_port = int(os.getenv("DB_PORT", 5432))
db_name = os.getenv('DB_NAME')
db_username = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')

#os.environ["OPENAI_API_KEY"]=os.getenv("AZURE_OPENAI_API_KEY")

encoded_password = urllib.parse.quote_plus(db_password)

#connection_string = f"postgresql://{db_username}:{encoded_password}@{db_host}:{db_port}/{db_name}"

def get_pg_connection():
    return psycopg2.connect(
        dbname=db_name,
        user=db_username,
        password=db_password,
        host=db_host,
        port=db_port
    )

#engine = create_engine(connection_string)

# llm = AzureChatOpenAI(
#     azure_deployment=os.getenv("AZURE_DEPLOYMENT_NAME"),
#     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#     openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#     openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
#  #   model_name=f"azure/{os.getenv('AZURE_DEPLOYMENT_NAME')}",
#     # deployment_model=f"azure/{os.getenv('"EMBEDDING_MODEL"')}",
#     max_retries=3,
#     timeout=30
# )

llm = LLM(
    model=f"azure/{os.getenv('AZURE_DEPLOYMENT_NAME')}",
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)


embedding_model = AzureOpenAIEmbeddings(
                model=os.getenv("AZURE_EMBEDDING_MODEL"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_EMBED"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY_EMBED"),
                openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION_EMBED"),
                deployment=os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME")
            )

# Initialize the tool with the database URI and the target table name
# pg_search_tool = PGSearchTool(
#     db_uri=connection_string, 
#     table_name='embeddings'
# )

def search_similar_documents_pgvector(query: str, k: int = 8, threshold: float = 0.3) -> list[Document]:
    query_embedding = embedding_model.embed_query(query)
    embedding_str = "[" + ",".join([str(x) for x in query_embedding]) + "]"
    distance_threshold = 1 - threshold

    sql = f"""
        SELECT
            id, content, source, source_url, title,
            1 - (embedding <=> %s::vector) AS similarity
        FROM embeddings
        WHERE embedding <=> %s::vector < {distance_threshold}
        ORDER BY embedding <=> %s::vector
        LIMIT {k}
    """

    try:
        conn = get_pg_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, (embedding_str, embedding_str, embedding_str))
                rows = cur.fetchall()

        docs = []
        for row in rows:
            doc = Document(
                page_content=row[1],
                metadata={
                    "id": row[0],
                    "source": row[2],
                    "source_url": row[3],
                    "title": row[4],
                    "similarity": row[5]
                }
            )
            docs.append(doc)

        return docs

    except Exception as e:
        print(" Failed to retrieve chunks from PostgreSQL:", e)
        return []

pg_search_agent = Agent(
    role=dedent((
        """
        Migration Pathway Advisor
        """)), # Think of this as the job title
    backstory=dedent((
        """
        You are a senior migration advisor with 15+ years of experience helping people 
        navigate complex migration processes. You specialize in legal pathways, visa requirements, 
        and procedural guidance. You always prioritize safe, legal migration routes and warn against 
        dangerous alternatives.
        """)), # This is the backstory of the agent, this helps the agent to understand the context of the task
    goal=dedent((
        """
        Provide comprehensive migration pathway advice based on user's origin, destination, and circumstances.
        """)), # This is the goal that the agent is trying to achieve
    allow_delegation=False,
    verbose=True,
    # ↑ Whether the agent execution should be in verbose mode
    max_iter=3,
    # ↑ maximum number of iterations the agent can perform before being forced to give its best answer (generate the output)
    max_rpm=100, # This is the maximum number of requests per minute that the agent can make to the language model
    llm=llm
)

pg_search_task = Task(
    description=dedent((
        """
       Analyze the user's migration query and context to understand their specific needs:
            
            User Query: {user_query}
            User Context: {user_context}
            
            Your analysis should:
            1. Identify the type of migration inquiry (visa, asylum, family reunification, etc.)
            2. Determine the user's current location and intended destination
            3. Assess the urgency and complexity of the request
            4. Identify any potential risks or red flags
            5. Categorize the primary assistance needed
            
            Provide a structured analysis that other agents can use to provide targeted assistance.
        """)),
    expected_output=dedent((
        """
        A structured analysis categorizing the migration request with key details and recommendations for specialized assistance.
        """)),
    agent=pg_search_agent
    # ↑ The output of each task iteration will be saved here
)


def main():


    # Instantiate your crew with a sequential process
    crew = Crew(
        agents=[pg_search_agent],
        tasks=[pg_search_task],
        verbose=True,  # You can set it to True or False
        # ↑ indicates the verbosity level for logging during execution.
        process=Process.sequential
        # ↑ the process flow that the crew will follow (e.g., sequential, hierarchical).
    )

    user_query = "I want to migrate from Senegal to Canada for work. What are my options?"    
    documents = search_similar_documents_pgvector(user_query, k=15, threshold=0.2)

    processed_context = []
    for doc in documents:
        doc_info = {
            "content": doc.page_content,
            "metadata": doc.metadata
        }
        processed_context.append(doc_info)

    print(processed_context)

    inputs = {
    "user_query": user_query,
    "user_context": processed_context
    }

    

    result = crew.kickoff(inputs=inputs)
    print("\n\n########################")
    print("## Here is your custom crew run result:")
    print("########################\n")
    print(result.raw)


if __name__ == "__main__":
  main()
     