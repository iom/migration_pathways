# crew.py - CrewAI Crew Configuration for Migration Assistance
from crewai import Crew, Process
from crew_ai.agents import MigrationAgents
from crew_ai.tasks import MigrationTasks
from crew_ai.tools import get_migration_tools
import json
from langchain_openai import AzureOpenAIEmbeddings
from langchain_core.documents import Document
import psycopg2 
import os
from dotenv import load_dotenv
from utility.json_loader import load_json_knowledge, format_json_knowledge_as_text

load_dotenv()

class MigrationAssistanceCrew:
    """Main crew orchestrator for migration assistance"""
    
    def __init__(self):
        self.agents = MigrationAgents()
        self.tasks = MigrationTasks()
        self.tools = get_migration_tools()
        self.db_host = os.getenv('DB_HOST')
        self.db_port = int(os.getenv("DB_PORT", 5432))
        self.db_name = os.getenv('DB_NAME')
        self.db_username = os.getenv('DB_USERNAME')
        self.db_password = os.getenv('DB_PASSWORD')
        self.embedding_model = AzureOpenAIEmbeddings(
                model=os.getenv("AZURE_EMBEDDING_MODEL"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_EMBED"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY_EMBED"),
                openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION_EMBED"),
                deployment=os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME")
            )


    def get_pg_connection(self):
        return psycopg2.connect(
            dbname=self.db_name,
            user=self.db_username,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port
        )
    
    def search_similar_documents_pgvector(self, query: str, k: int = 8, threshold: float = 0.3) -> list[Document]:
        query_embedding = self.embedding_model.embed_query(query)
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
            conn = self.get_pg_connection()
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
    
    def get_docs_context(self, docs: list[Document]) -> dict:
            processed_context = []
            for doc in docs:
                doc_info = {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                processed_context.append(doc_info)

            return processed_context


    def create_crew(self, user_query: str, user_context: dict):
        """Create and configure the crew for a specific migration query"""
        
        # Initialize agents with tools
        migration_advisor = self.agents.migration_advisor_agent()
        # risk_assessor = self.agents.risk_assessment_agent()
        # doc_specialist = self.agents.documentation_specialist_agent()
        # cultural_advisor = self.agents.cultural_integration_agent()
        # employment_advisor = self.agents.employment_advisor_agent()
        # resource_coordinator = self.agents.resource_coordinator_agent()
        
        # Assign tools to relevant agents
        # migration_advisor.tools = self.tools
        # risk_assessor.tools = [self.tools[2]]  # Risk assessment tool
        # doc_specialist.tools = [self.tools[0]]  # Knowledge search tool
        # resource_coordinator.tools = [self.tools[1]]  # Contact search tool

        query_parts = user_query.split(" and ")

        k = 8
        threshold = 0.3

        if len(query_parts) > 1:
            k = 15
            threshold = 0.2

     
        documents = self.search_similar_documents_pgvector(user_query, k, threshold)
        docs_context = self.get_docs_context(documents)

        json_knowledge = load_json_knowledge()
        iom_office_context = format_json_knowledge_as_text(json_knowledge)
        
        # Create tasks
        analysis_task = self.tasks.analyze_migration_request(migration_advisor, user_query, user_context, docs_context, iom_office_context)
        # risk_task = self.tasks.assess_migration_risks(risk_assessor, user_query, user_context)
        # doc_task = self.tasks.provide_legal_documentation_guidance(doc_specialist, user_query, user_context)
        # cultural_task = self.tasks.provide_cultural_integration_advice(cultural_advisor, user_query, user_context)
        # employment_task = self.tasks.provide_employment_guidance(employment_advisor, user_query, user_context)
        # resource_task = self.tasks.coordinate_resources_and_contacts(resource_coordinator, user_query, user_context)
        
        # Final synthesis task
        # synthesis_task = self.tasks.synthesize_comprehensive_response(
        #     migration_advisor, 
        #     user_query, 
        #     "Results from all specialized agents"
        # )
        
        # Create crew
        crew = Crew(
            agents=[
                migration_advisor,
                # risk_assessor,
                # doc_specialist,
                # cultural_advisor,
                # employment_advisor,
                # resource_coordinator
            ],
            tasks=[
                analysis_task,
                # risk_task,
                # doc_task,
                # cultural_task,
                # employment_task,
                # resource_task,
                # synthesis_task
            ],
            process=Process.sequential,
            verbose=True,
            memory=True,
            max_rpm=10,  # Rate limiting
            share_crew=False,
            embedder={
                "provider": "azure",
                "config": {
                    "model": os.getenv("AZURE_EMBEDDING_MODEL"),
                    "deployment_id": os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME"),
                    "api_key": os.getenv("AZURE_OPENAI_API_KEY_EMBED"),
                    "api_base": os.getenv("AZURE_OPENAI_ENDPOINT_EMBED"),
                    "api_version": os.getenv("AZURE_OPENAI_API_VERSION_EMBED")
                }
            }
        )
        
        return crew
    
   
    # def get_simplified_crew(self, user_query: str, user_context: dict):
    #     """Create a simplified crew for basic queries"""
        
    #     # Initialize key agents
    #     migration_advisor = self.agents.migration_advisor_agent()
    #     risk_assessor = self.agents.risk_assessment_agent()
    #     resource_coordinator = self.agents.resource_coordinator_agent()
        
    #     # Assign tools
    #     migration_advisor.tools = self.tools
    #     risk_assessor.tools = [self.tools[2]]  # Risk assessment tool
    #     resource_coordinator.tools = [self.tools[1]]  # Contact search tool
        
    #     # Create simplified tasks
    #     analysis_task = self.tasks.analyze_migration_request(migration_advisor, user_query, user_context)
    #     risk_task = self.tasks.assess_migration_risks(risk_assessor, user_query, user_context)
    #     resource_task = self.tasks.coordinate_resources_and_contacts(resource_coordinator, user_query, user_context)
        
    #     # Synthesis task
    #     synthesis_task = self.tasks.synthesize_comprehensive_response(
    #         migration_advisor, 
    #         user_query, 
    #         "Results from specialized agents"
    #     )
        
    #     # Create simplified crew
    #     crew = Crew(
    #         agents=[migration_advisor, risk_assessor, resource_coordinator],
    #         tasks=[analysis_task, risk_task, resource_task, synthesis_task],
    #         process=Process.sequential,
    #         verbose=True,
    #         memory=True,
    #         max_rpm=15,
    #         share_crew=False
    #     )
        
    #     return crew
    
    # def determine_crew_complexity(self, user_query: str, user_context: dict) -> str:
    #     """Determine whether to use full or simplified crew based on query complexity"""
        
    #     complex_keywords = [
    #         "employment", "job", "work", "visa", "documentation", "documents", 
    #         "cultural", "integration", "adapt", "language", "multiple", "several",
    #         "comprehensive", "detailed", "everything", "all information"
    #     ]
        
    #     query_lower = user_query.lower()
    #     complexity_score = sum(1 for keyword in complex_keywords if keyword in query_lower)
        
    #     # Check if user has specific context that suggests complex needs
    #     if user_context:
    #         source_country = user_context.get("source_country")
    #         destination_country = user_context.get("destination_country")
    #         if source_country and destination_country:
    #             complexity_score += 1
    #     #print(complexity_score)        
        
    #     return "full" if complexity_score >= 2 else "simplified"
    
    def process_migration_query(self, user_query: str, user_context: dict = None) -> str:
        """Main entry point for processing migration queries"""
        
        if not user_context:
            user_context = {}
        
        try:
            # # Determine crew complexity
            # crew_type = self.determine_crew_complexity(user_query, user_context)
            
            # # Create appropriate crew
            # if crew_type == "full":
            #     crew = self.create_crew(user_query, user_context)
            # else:
            #     crew = self.get_simplified_crew(user_query, user_context)
            
            # Execute crew
            crew = self.create_crew(user_query, user_context)
            result = crew.kickoff()
            
            return str(result)
            
        except Exception as e:
            error_msg = f"Error processing migration query: {str(e)}"
            print(f"[CREW AI ERROR] {error_msg}")
            
            # Fallback response
            return """I apologize, but I encountered an issue processing your request with our specialized migration assistance system. 
            However, I can still help you with basic migration information. Please try rephrasing your question, 
            or contact your nearest IOM office for direct assistance."""
    
    def get_user_context_from_db(self, user_email: str, engine) -> dict:
        """Extract user context from database"""
        try:
            from sqlalchemy import text
            with engine.connect() as connection:
                result = connection.execute(
                    text("SELECT source_country, destination_country FROM users WHERE email = :email"),
                    {"email": user_email}
                )
                user_data = result.fetchone()
                
                if user_data:
                    return {
                        "source_country": user_data[0],
                        "destination_country": user_data[1]
                    }
                return {}
        except Exception as e:
            print(f"[ERROR] Failed to get user context: {str(e)}")
            return {}