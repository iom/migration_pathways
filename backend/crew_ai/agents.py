# agents.py - CrewAI Agent Definitions for Migration Assistance
from crewai import Agent, LLM
from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class MigrationAgents:
    """Migration assistance agents with specialized roles"""
    
    def __init__(self):
        self.llm = LLM(
            model=f"azure/{os.getenv('AZURE_DEPLOYMENT_NAME')}",
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            )
    
    def migration_advisor_agent(self):
        """Primary migration advisor specializing in pathways and procedures"""
        return Agent(
            role="Migration Pathway Advisor",
            goal="Provide comprehensive migration advice based on given input",
            backstory="""You are a senior migration advisor with 15+ years of experience helping people 
            guiding them in migration topics.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm,
            tools=[],  # Will be populated with RAG tools
            max_iter=3
        )
    
    # def risk_assessment_agent(self):
    #     """Agent focused on identifying and warning about migration risks"""
    #     return Agent(
    #         role="Migration Risk Assessment Specialist",
    #         goal="Identify potential risks, scams, and dangerous migration practices to keep users safe",
    #         backstory="""You are a migration security expert who has studied human trafficking patterns, 
    #         smuggling networks, and migration-related crimes. Your primary concern is user safety. You 
    #         excel at detecting red flags in migration offers and educating users about legitimate vs 
    #         fraudulent services.""",
    #         verbose=True,
    #         allow_delegation=False,
    #         llm=self.llm,
    #         tools=[],
    #         max_iter=2
    #     )
    
    # def documentation_specialist_agent(self):
    #     """Agent specializing in required documents and paperwork"""
    #     return Agent(
    #         role="Documentation and Legal Requirements Specialist",
    #         goal="Provide detailed guidance on required documents, applications, and legal compliance",
    #         backstory="""You are a meticulous legal documentation expert who has helped thousands of 
    #         migrants prepare their paperwork correctly. You know the specific requirements for different 
    #         countries, visa types, and application processes. You help users understand what documents 
    #         they need and how to obtain them properly.""",
    #         verbose=True,
    #         allow_delegation=False,
    #         llm=self.llm,
    #         tools=[],
    #         max_iter=2
    #     )
    
    # def cultural_integration_agent(self):
    #     """Agent helping with cultural adaptation and integration"""
    #     return Agent(
    #         role="Cultural Integration Advisor",
    #         goal="Help users understand cultural differences and prepare for successful integration",
    #         backstory="""You are a cultural anthropologist and integration specialist who has lived in 
    #         multiple countries and helped migrants adapt to new cultures. You understand the challenges 
    #         of cultural adaptation and provide practical advice for successful integration, including 
    #         language learning, cultural norms, and community resources.""",
    #         verbose=True,
    #         allow_delegation=False,
    #         llm=self.llm,
    #         tools=[],
    #         max_iter=2
    #     )
    
    # def employment_advisor_agent(self):
    #     """Agent specializing in employment and economic opportunities"""
    #     return Agent(
    #         role="Employment and Economic Opportunity Advisor",
    #         goal="Provide guidance on job markets, skill recognition, and economic integration",
    #         backstory="""You are a career counselor and labor market expert who specializes in helping 
    #         migrants find employment and economic opportunities. You understand credential recognition 
    #         processes, job market trends, and how to match migrant skills with destination country 
    #         opportunities.""",
    #         verbose=True,
    #         allow_delegation=False,
    #         llm=self.llm,
    #         tools=[],
    #         max_iter=2
    #     )
    
    # def resource_coordinator_agent(self):
    #     """Agent that coordinates resources and provides contact information"""
    #     return Agent(
    #         role="Resource Coordination Specialist",
    #         goal="Connect users with relevant IOM offices, NGOs, and support services",
    #         backstory="""You are a resource coordinator who maintains an extensive network of migration 
    #         support organizations, IOM offices, legal aid services, and NGOs. You excel at matching 
    #         users with the right resources based on their location and specific needs.""",
    #         verbose=True,
    #         allow_delegation=False,
    #         llm=self.llm,
    #         tools=[],  # Will include JSON knowledge base tool
    #         max_iter=2
    #     )