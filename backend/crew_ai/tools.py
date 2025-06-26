# tools.py - CrewAI Tools for Migration Assistance

from crewai.tools import BaseTool
from typing import Type, Optional, List
from pydantic import BaseModel, Field, PrivateAttr
import os
from langchain_openai import AzureOpenAIEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import traceback

load_dotenv()

os.environ["CHROMA_OPENAI_API_KEY"] = os.getenv("AZURE_EMBEDDING_MODEL")

class VectorSearchInput(BaseModel):
    """Input for vector search tool"""
    query: str = Field(description="Search query for migration information")

class ContactSearchInput(BaseModel):
    """Input for contact search tool"""
    location: str = Field(description="Location or country to find IOM contacts")
    service_type: str = Field(description="Type of service needed (optional)", default="")



class MigrationKnowledgeSearchTool(BaseTool):
    """Tool for searching migration knowledge base using vector similarity with pgvector"""
    name: str = "Migration Knowledge Search"
    description: str = "Search the migration knowledge base for relevant information about procedures, policies, and guidance"
    args_schema: Type[BaseModel] = VectorSearchInput
    
    # Use PrivateAttr for internal attributes
    _embedding_model: Optional[AzureOpenAIEmbeddings] = PrivateAttr(default=None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._initialize_components()
    
    def _get_pg_connection(self):
        """Get PostgreSQL connection with proper error handling"""
        try:
            # Debug: Print connection parameters (remove in production)
            print(f"Connecting to PostgreSQL:")
            print(f"Host: {os.getenv('DB_HOST')}")
            print(f"Port: {os.getenv('DB_PORT', 5432)}")
            print(f"Database: {os.getenv('DB_NAME')}")
            print(f"User: {os.getenv('DB_USERNAME')}")
            
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                port=int(os.getenv("DB_PORT", 5432)),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USERNAME"),
                password=os.getenv("DB_PASSWORD"),
                connect_timeout=10
            )
            print("PostgreSQL connection successful")
            return conn
        except Exception as e:
            print(f"Failed to connect to PostgreSQL: {e}")
            raise Exception(f"PostgreSQL connection failed: {e}")
    
    def _search_similar_documents_pgvector(self, query: str, k: int = 8, threshold: float = 0.3) -> List[Document]:
        """Search similar documents using pgvector with enhanced error handling"""
        try:
            print(f"Starting vector search for query: {query[:50]}...")
            
            # Generate embedding
            query_embedding = self._embedding_model.embed_query(query)
            embedding_str = "[" + ",".join([str(x) for x in query_embedding]) + "]"
            distance_threshold = 1 - threshold
            
            print(f"Generated embedding with {len(query_embedding)} dimensions")
            
            sql = f"""
                SELECT
                    id, content, source, source_url, title,
                    1 - (embedding <=> %s::vector) AS similarity
                FROM embeddings
                WHERE embedding <=> %s::vector < {distance_threshold}
                ORDER BY embedding <=> %s::vector
                LIMIT {k}
            """
            
            print("Executing PostgreSQL query...")
            conn = self._get_pg_connection()
            with conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (embedding_str, embedding_str, embedding_str))
                    rows = cur.fetchall()
            
            print(f"Found {len(rows)} matching documents")
            
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
        
        except psycopg2.Error as e:
            print(f"PostgreSQL error: {e}")
            print(f"Error code: {e.pgcode}")
            print(f"Error details: {e.pgerror}")
            return []
        except Exception as e:
            print(f"Failed to retrieve chunks from PostgreSQL: {e}")
            print(f"Full traceback: {traceback.format_exc()}")
            return []
    
    def _initialize_components(self):
        """Initialize the embedding model with enhanced error handling"""
        try:
            print("Initializing Azure OpenAI embedding model...")
            
            # Validate required environment variables
            required_vars = [
                "AZURE_EMBEDDING_MODEL",
                "AZURE_OPENAI_ENDPOINT_EMBED", 
                "AZURE_OPENAI_API_KEY_EMBED",
                "AZURE_OPENAI_API_VERSION_EMBED",
                "AZURE_EMBEDDING_DEPLOYMENT_NAME"
            ]
            
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            if missing_vars:
                raise ValueError(f"Missing required environment variables: {missing_vars}")
            
            # Validate PostgreSQL variables
            pg_vars = ["DB_HOST", "DB_NAME", "DB_USERNAME", "DB_PASSWORD"]
            missing_pg_vars = [var for var in pg_vars if not os.getenv(var)]
            if missing_pg_vars:
                raise ValueError(f"Missing required PostgreSQL environment variables: {missing_pg_vars}")
            
            self._embedding_model = AzureOpenAIEmbeddings(
                model=os.getenv("AZURE_EMBEDDING_MODEL"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_EMBED"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY_EMBED"),
                openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION_EMBED"),
                deployment=os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME")
            )
            print("Embedding model initialized successfully")
            
            # Test PostgreSQL connection
            test_conn = self._get_pg_connection()
            test_conn.close()
            print("PostgreSQL connection test successful")
            
        except Exception as e:
            print(f"Error initializing components: {e}")
            print(f"Full traceback: {traceback.format_exc()}")
            self._embedding_model = None
    
    def _run(self, query: str) -> str:
        """Search the PostgreSQL vector database for relevant migration information"""
        try:
            if not self._embedding_model:
                return "Embedding model not initialized. Please check your configuration."
            
            # Perform similarity search using pgvector
            docs = self._search_similar_documents_pgvector(
                query=query,
                k=8,
                threshold=0.3
            )
            
            if not docs:
                return "No relevant information found in the knowledge base for this query."
            
            # Format results
            results = []
            for i, doc in enumerate(docs):
                source = doc.metadata.get("source_url", doc.metadata.get("source", "Unknown"))
                title = doc.metadata.get("title", "N/A")
                similarity = doc.metadata.get("similarity", 0)
                content = doc.page_content[:500].strip()
                
                results.append(f"Source {i+1}: {title}\nURL: {source}\nSimilarity: {similarity:.3f}\nContent: {content}...\n")
            
            return "\n".join(results)
            
        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"

class IOMContactSearchTool(BaseTool):
    """Tool for finding IOM office contacts and resources"""
    name: str = "IOM Contact Search"
    description: str = "Find IOM office contacts, phone numbers, and email addresses by location"
    args_schema: Type[BaseModel] = ContactSearchInput
    
    # Use PrivateAttr for internal attributes
    _contacts_file: Optional[str] = PrivateAttr(default=None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._contacts_file = os.path.join(os.path.dirname(__file__), "..", "knowledge", "iom_office_contact.json")
    
    def _run(self, location: str, service_type: str = "") -> str:
        """Search for IOM contacts by location"""
        try:
            if not os.path.exists(self._contacts_file):
                return f"Contacts file not found at: {self._contacts_file}"
            
            with open(self._contacts_file, 'r', encoding='utf-8') as f:
                contacts_data = json.load(f)
            
            # Search for matching locations
            results = []
            location_lower = location.lower()
            
            for contact in contacts_data:
                # Check if location matches country, city, or office name
                if (location_lower in contact.get("country", "").lower() or 
                    location_lower in contact.get("city", "").lower() or
                    location_lower in contact.get("office_name", "").lower()):
                    
                    contact_info = f"""
Office: {contact.get('office_name', 'N/A')}
Country: {contact.get('country', 'N/A')}
City: {contact.get('city', 'N/A')}
Address: {contact.get('address', 'N/A')}
Phone: {contact.get('phone', 'N/A')}
Email: {contact.get('email', 'N/A')}
Services: {contact.get('services', 'N/A')}
"""
                    results.append(contact_info)
            
            if not results:
                return f"No IOM office contacts found for location: {location}"
            
            return f"IOM Office Contacts for {location}:\n\n" + "\n---\n".join(results)
            
        except Exception as e:
            return f"Error searching IOM contacts: {str(e)}"

class MigrationRiskAssessmentTool(BaseTool):
    """Tool for assessing migration risks and red flags"""
    name: str = "Migration Risk Assessment"
    description: str = "Assess potential risks in migration scenarios and identify red flags"
    args_schema: Type[BaseModel] = VectorSearchInput
    
    def _run(self, query: str) -> str:
        """Assess risks in the migration scenario"""
        risk_keywords = {
            "trafficking": ["job offer", "modeling", "entertainment", "high pay", "no experience needed", "all expenses paid"],
            "smuggling": ["guaranteed crossing", "secret route", "no documents needed", "fast crossing"],
            "fraud": ["visa guarantee", "100% success", "pay after arrival", "special connections"],
            "exploitation": ["work without pay", "keep documents", "isolated location", "debt bondage"]
        }
        
        query_lower = query.lower()
        detected_risks = []
        
        for risk_type, keywords in risk_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    detected_risks.append(f"⚠️ {risk_type.upper()} RISK: Presence of '{keyword}' phrase")
        
        if not detected_risks:
            return "No immediate red flags detected, but always verify migration services through official channels."
        
        warning = "🚨 POTENTIAL RISKS DETECTED:\n\n" + "\n".join(detected_risks)
        warning += "\n\n⚠️ SAFETY RECOMMENDATIONS:\n"
        warning += "• Only use official government channels and verified services\n"
        warning += "• Never pay large sums upfront or give up your documents\n"
        warning += "• Be suspicious of 'too good to be true' offers\n"
        warning += "• Contact IOM or local authorities if you suspect fraud\n"
        warning += "• Always verify credentials of migration service providers"
        
        return warning

def get_migration_tools():
    """Return list of all migration tools"""
    return [
        MigrationKnowledgeSearchTool(),
        IOMContactSearchTool(),
        MigrationRiskAssessmentTool()
    ]