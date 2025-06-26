# tasks.py - CrewAI Task Definitions for Migration Assistance

from crewai import Task

class MigrationTasks:
    """Task definitions for migration assistance crew"""
    
    def analyze_migration_request(self, agent, user_query, user_context, docs_context, iom_office_context):
        """Initial analysis of user's migration request"""
        return Task(
            description=f"""
            Analyze the user's migration query and context to understand their specific needs. 
            ONLY use the information provided between <context> tags — DO NOT use external knowledge, or your training data or assumptions.
            
            <context>
            User Query: {user_query}
            User Context: {user_context}
            Knowledge Base Context: {docs_context}
            IOM Offices Context: {iom_office_context}
            </context>
            
            Your analysis and response should Follow these rules:
            1. For each part of a multi-question query, answer independently.
            2. Use Knowledge Base Context for migration questions.
            3. If no CONTEXT or RELEVANT info is found, respond: "Sorry, I don’t have enough information in the provided context to answer that.
            4. DO NOT guess, infer, or use unrelated context.
            5. Ignore unrelated, unethical, or non-migration questions.
            6. RESPONSE should be empathetic in nature.
            7. RESPONSE should be interactive in nature - include follow-up questions, offer next steps, suggest related topics they might want to explore, or prompt the user to provide additional details that would help give more targeted assistance.

            Provide a response to provide targeted assistance. Keep the response concise and more human in nature.
            """,
            agent=agent,
            expected_output="A structured response for specialized assistance."
        )
    
    # def assess_migration_risks(self, agent, user_query, user_context):
    #     """Risk assessment for the migration scenario"""
    #     return Task(
    #         description=f"""
    #         Conduct a comprehensive risk assessment for this migration scenario:
            
    #         User Query: {user_query}
    #         User Context: {user_context}
            
    #         Evaluate:
    #         1. Potential trafficking or smuggling risks
    #         2. Fraudulent service providers or scams
    #         3. Unsafe migration routes or methods
    #         4. Legal risks and compliance issues
    #         5. Financial risks and exploitation potential
            
    #         Provide specific warnings and safe alternatives where applicable.
    #         """,
    #         agent=agent,
    #         expected_output="A detailed risk assessment with specific warnings about potential dangers and recommendations for safe alternatives."
    #     )
    
    # def provide_legal_documentation_guidance(self, agent, user_query, user_context):
    #     """Legal and documentation requirements task"""
    #     return Task(
    #         description=f"""
    #         Provide detailed guidance on legal requirements and documentation:
            
    #         User Query: {user_query}
    #         User Context: {user_context}
            
    #         Cover:
    #         1. Required documents and applications
    #         2. Legal procedures and timelines
    #         3. Costs and fees involved
    #         4. Where to obtain necessary documents
    #         5. Common mistakes to avoid
            
    #         Be specific about requirements for the user's situation.
    #         """,
    #         agent=agent,
    #         expected_output="Comprehensive documentation checklist with step-by-step guidance on legal requirements and procedures."
    #     )
    
    # def provide_cultural_integration_advice(self, agent, user_query, user_context):
    #     """Cultural integration and adaptation guidance"""
    #     return Task(
    #         description=f"""
    #         Provide cultural integration advice for successful adaptation:
            
    #         User Query: {user_query}
    #         User Context: {user_context}
            
    #         Address:
    #         1. Cultural differences and expectations
    #         2. Language learning resources
    #         3. Community integration strategies
    #         4. Social norms and customs
    #         5. Support networks and communities
            
    #         Focus on practical advice for successful integration.
    #         """,
    #         agent=agent,
    #         expected_output="Practical cultural integration advice with specific resources and strategies for successful adaptation."
    #     )
    
    # def provide_employment_guidance(self, agent, user_query, user_context):
    #     """Employment and economic opportunity guidance"""
    #     return Task(
    #         description=f"""
    #         Provide employment and economic opportunity guidance:
            
    #         User Query: {user_query}
    #         User Context: {user_context}
            
    #         Include:
    #         1. Job market conditions and opportunities
    #         2. Skill recognition and credential validation
    #         3. Professional licensing requirements
    #         4. Job search strategies and resources
    #         5. Economic integration pathways
            
    #         Tailor advice to the user's background and destination.
    #         """,
    #         agent=agent,
    #         expected_output="Employment guidance with specific opportunities, requirements, and strategies for economic integration."
    #     )
    
    # def coordinate_resources_and_contacts(self, agent, user_query, user_context):
    #     """Resource coordination and contact information"""
    #     return Task(
    #         description=f"""
    #         Coordinate relevant resources and provide contact information:
            
    #         User Query: {user_query}
    #         User Context: {user_context}
            
    #         Provide:
    #         1. Relevant IOM office contacts
    #         2. Local NGO and support organization contacts
    #         3. Legal aid resources
    #         4. Government agency contacts
    #         5. Community support services
            
    #         Match resources to the user's specific location and needs.
    #         """,
    #         agent=agent,
    #         expected_output="List of relevant contacts and resources with specific information on how to access support services."
    #     )
    
    # def synthesize_comprehensive_response(self, agent, user_query, analysis_results):
    #     """Final synthesis of all agent responses"""
    #     return Task(
    #         description=f"""
    #         Synthesize all the analysis and recommendations into a comprehensive, user-friendly response:
            
    #         Original User Query: {user_query}
    #         Agent Analysis Results: {analysis_results}
            
    #         Create a response that:
    #         1. Directly addresses the user's question
    #         2. Incorporates risk warnings and safety guidance
    #         3. Provides actionable next steps
    #         4. Includes relevant resources and contacts
    #         5. Is empathetic and supportive in tone
    #         6. Prioritizes legal and safe migration pathways
            
    #         Format the response in a clear, structured manner that's easy to understand.
    #         """,
    #         agent=agent,
    #         expected_output="A comprehensive, well-structured response that addresses the user's needs while prioritizing safety and legal compliance."
    #     )