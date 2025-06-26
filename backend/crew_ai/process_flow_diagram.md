# CrewAI Backend Process Flow

## Complete Process Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              USER REQUEST                                      │
└─────────────────┬───────────────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        FLASK ROUTE HANDLER                                     │
│  /api/chat/crew (CrewAI)  │  /api/chat/hybrid (Fallback)  │  /api/chat (RAG)  │
└─────────────────┬───────────────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     AUTHENTICATION & VALIDATION                                │
│  • Check JWT token       • Validate user status      • Update request count   │
└─────────────────┬───────────────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      USER CONTEXT EXTRACTION                                   │
│  • Get source_country    • Get destination_country    • Get conversation_history│
└─────────────────┬───────────────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    CREW COMPLEXITY DETERMINATION                               │
│  Query Analysis: "employment", "visa", "comprehensive", etc.                   │
│  Context Score: source_country + destination_country presence                  │
│  Decision: SIMPLIFIED CREW (3 agents) vs FULL CREW (6 agents)                 │
└─────────────────┬───────────────────────────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌─────────────────┐  ┌─────────────────┐
│ SIMPLIFIED CREW │  │   FULL CREW     │
│   (3 Agents)    │  │   (6 Agents)    │
└─────────────────┘  └─────────────────┘
        │                   │
        └─────────┬─────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CREW INITIALIZATION                                  │
│  1. Create Agent Instances  2. Assign Tools to Agents  3. Create Task Queue   │
└─────────────────┬───────────────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SEQUENTIAL TASK EXECUTION                              │
└─────────────────┬───────────────────────────────────────────────────────────────┘
                  │
                  ▼
              [TASK 1]
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    MIGRATION REQUEST ANALYSIS                                  │
│  Agent: Migration Pathway Advisor                                              │
│  Tools: All tools (Vector Search, Contact Search, Risk Assessment)             │
│  Output: Structured analysis of migration request type and complexity          │
└─────────────────┬───────────────────────────────────────────────────────────────┘
                  │
                  ▼
              [TASK 2]
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      RISK ASSESSMENT                                           │
│  Agent: Risk Assessment Specialist                                             │
│  Tools: Risk Assessment Tool                                                   │
│  Output: Safety warnings, red flags, dangerous practice identification         │
└─────────────────┬───────────────────────────────────────────────────────────────┘
                  │
                  ▼
         [CONDITIONAL TASKS - Based on Crew Type]
┌─────────────────────────────────────────────────────────────────────────────────┐
│  FULL CREW ONLY:                                                               │
│  [TASK 3] Documentation Guidance (Documentation Specialist + Vector Search)   │
│  [TASK 4] Cultural Integration (Cultural Advisor)                              │
│  [TASK 5] Employment Guidance (Employment Advisor)                             │
└─────────────────┬───────────────────────────────────────────────────────────────┘
                  │
                  ▼
              [TASK 6/3]
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    RESOURCE COORDINATION                                       │
│  Agent: Resource Coordinator                                                   │
│  Tools: IOM Contact Search Tool                                                │
│  Output: Relevant IOM offices, NGOs, support services                          │
└─────────────────┬───────────────────────────────────────────────────────────────┘
                  │
                  ▼
            [FINAL TASK]
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      RESPONSE SYNTHESIS                                        │
│  Agent: Migration Pathway Advisor                                              │
│  Input: All previous task outputs                                              │
│  Output: Comprehensive, user-friendly final response                           │
└─────────────────┬───────────────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      CONVERSATION MANAGEMENT                                   │
│  • Store user query + AI response in session_contexts                          │
│  • Maintain conversation history (max 20 messages)                             │
│  • Track processing time and metadata                                          │
└─────────────────┬───────────────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        RESPONSE TO USER                                        │
│  • JSON response with assistant message                                        │
│  • Processing time metadata                                                    │
│  • CrewAI execution confirmation                                               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Detailed Step-by-Step Process

### 1. Request Reception (`chat_crew_ai.py:62`)
```python
@crew_chat_blueprint.route("/api/chat/crew", methods=["POST"])
@token_required
def crew_chat(user_email):
```

### 2. User Context Gathering (`crew.py:109`)
```python
user_context = migration_crew.get_user_context_from_db(user_email, engine)
conversation_history = crew_session_contexts.get(user_email, [])
```

### 3. Crew Complexity Decision (`crew.py:53`)
```python
crew_type = self.determine_crew_complexity(user_query, user_context)
# Returns "full" or "simplified" based on:
# - Complex keywords count (employment, visa, documentation, etc.)
# - User context completeness (source + destination countries)
```

### 4. Agent and Tool Initialization
#### Simplified Crew (3 agents):
```python
migration_advisor = self.agents.migration_advisor_agent()
risk_assessor = self.agents.risk_assessment_agent()  
resource_coordinator = self.agents.resource_coordinator_agent()

# Tool assignment
migration_advisor.tools = [Vector Search, Contact Search, Risk Assessment]
risk_assessor.tools = [Risk Assessment]
resource_coordinator.tools = [Contact Search]
```

#### Full Crew (6 agents):
```python
# All agents initialized with specialized tool assignments
```

### 5. Task Creation and Execution Queue
```python
tasks = [
    analyze_migration_request,
    assess_migration_risks,
    # [Optional: doc_guidance, cultural_advice, employment_advice]
    coordinate_resources,
    synthesize_response
]
```

### 6. Sequential Agent Execution

#### Task 1: Migration Analysis
```python
Agent: Migration Pathway Advisor
Tools Used: 
  - migration_knowledge_search_tool.run(user_query)
  - migration_risk_assessment_tool.run(user_query)
  
Process:
1. Vector search in Chroma DB for relevant migration info
2. Risk pattern detection
3. Analysis categorization
```

#### Task 2: Risk Assessment  
```python
Agent: Risk Assessment Specialist
Tools Used:
  - migration_risk_assessment_tool.run(user_query)
  
Process:
1. Keyword pattern matching for:
   - Trafficking indicators
   - Smuggling red flags
   - Fraudulent service markers
2. Safety recommendations generation
```

#### Task 3-5: Specialized Analysis (Full Crew Only)
```python
Documentation Specialist: Legal requirements research
Cultural Advisor: Integration guidance
Employment Advisor: Job market analysis
```

#### Task 6: Resource Coordination
```python
Agent: Resource Coordinator
Tools Used:
  - iom_contact_search_tool.run(location=user_context.destination_country)
  
Process:
1. Search IOM office contacts by location
2. Match services to user needs
3. Provide contact details and services
```

#### Final Task: Synthesis
```python
Agent: Migration Pathway Advisor
Input: All previous task outputs
Process:
1. Combine all specialist recommendations
2. Structure user-friendly response
3. Prioritize safety and legal pathways
4. Include actionable next steps
```

### 7. Tool Execution Details

#### Vector Search Tool (`tools.py:35`)
```python
def _run(self, query: str) -> str:
    retriever = self.vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 8, "score_threshold": 0.3}
    )
    docs = retriever.get_relevant_documents(query)
    return formatted_results
```

#### Contact Search Tool (`tools.py:65`)
```python
def _run(self, location: str, service_type: str = "") -> str:
    # Load JSON knowledge base
    # Search by country/city/office name
    # Return formatted contact information
```

#### Risk Assessment Tool (`tools.py:95`)
```python
def _run(self, query: str) -> str:
    # Pattern matching against risk keywords
    # Generate warnings and recommendations
```

## Error Handling and Fallback Flow

```
CrewAI Execution
       │
       ▼
   [Try Block]
       │
   ┌───▼───┐
   │Success│────────────► Return CrewAI Response
   └───────┘
       │
   [Exception]
       │
       ▼
┌─────────────┐
│Log Error    │
│Print Details│
└─────┬───────┘
      │
      ▼
┌─────────────┐
│Return       │
│Fallback     │ ────────────► "Advanced system unavailable,
│Message      │                contact IOM office directly"
└─────────────┘
```

### Hybrid Endpoint Fallback (`chat_crew_ai.py:142`)
```python
try:
    crew_response = migration_crew.process_migration_query(...)
    return crew_response
except Exception as crew_error:
    # Fall back to original RAG system
    return basic_rag_response
```

## Performance Optimizations

### 1. Conversation Memory Management
```python
# Limit conversation history to prevent memory bloat
if len(crew_session_contexts[user_email]) > 20:
    crew_session_contexts[user_email] = crew_session_contexts[user_email][-20:]
```

### 2. Crew Complexity Optimization
```python
# Use fewer agents for simple queries
if complexity_score < 2:
    return "simplified"  # 3 agents, faster execution
else:
    return "full"        # 6 agents, comprehensive response
```

### 3. Rate Limiting Protection
```python
crew = Crew(
    max_rpm=15,  # Respect Azure OpenAI limits
    verbose=True,
    memory=True
)
```

This process flow ensures comprehensive, intelligent migration assistance while maintaining performance and reliability through intelligent crew selection and robust error handling.