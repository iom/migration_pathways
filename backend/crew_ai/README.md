# CrewAI Migration Assistant

This directory contains the CrewAI-based multi-agent system that enhances the migration chatbot with specialized AI agents.

## Architecture Overview

The CrewAI system consists of 6 specialized agents working collaboratively to provide comprehensive migration assistance:

### 🤖 Agents

1. **Migration Pathway Advisor** (`agents.py`)
   - Primary migration guidance and pathway recommendations
   - 15+ years experience persona
   - Prioritizes legal and safe migration routes

2. **Risk Assessment Specialist** (`agents.py`)
   - Identifies trafficking, smuggling, and fraud risks
   - Security expert persona with crime pattern knowledge
   - Provides safety warnings and alternatives

3. **Documentation Specialist** (`agents.py`)
   - Legal requirements and paperwork guidance
   - Meticulous legal expert persona
   - Knows specific country requirements

4. **Cultural Integration Advisor** (`agents.py`) 
   - Cultural adaptation and integration support
   - Anthropologist persona with multi-country experience
   - Practical cultural advice

5. **Employment Advisor** (`agents.py`)
   - Job markets and economic opportunities
   - Career counselor persona with labor market expertise
   - Credential recognition guidance

6. **Resource Coordinator** (`agents.py`)
   - IOM offices, NGOs, and support services
   - Resource coordinator persona with extensive network
   - Location-specific resource matching

### 🛠️ Tools

1. **Migration Knowledge Search Tool** (`tools.py`)
   - Vector similarity search in Chroma database
   - Retrieves relevant migration policies and procedures
   - Configurable similarity thresholds

2. **IOM Contact Search Tool** (`tools.py`)
   - Searches JSON knowledge base for IOM office contacts
   - Location-based contact matching
   - Provides phone, email, and service information

3. **Migration Risk Assessment Tool** (`tools.py`)
   - Automated risk detection using keyword patterns
   - Identifies trafficking, smuggling, fraud indicators
   - Provides safety recommendations

### 📋 Tasks

The system uses structured task definitions (`tasks.py`) for:
- Migration request analysis
- Risk assessment
- Documentation guidance
- Cultural integration advice
- Employment guidance
- Resource coordination
- Response synthesis

### 🎛️ Configuration

Settings in `config.py`:
- Azure OpenAI endpoints and API keys
- Agent execution parameters
- Tool configurations
- Rate limiting and timeout settings

## API Endpoints

### Primary CrewAI Chat
```
POST /api/chat/crew
```
Full CrewAI multi-agent response system.

### System Status
```
GET /api/chat/crew/status
```
Check CrewAI system health and availability.

### Reset Conversation
```
POST /api/chat/crew/reset
```
Clear user's conversation history.

### Hybrid Chat (Recommended)
```
POST /api/chat/hybrid
```
Intelligent system that tries CrewAI first, falls back to original RAG if needed.

## Usage Examples

### Simple Query
User: "What is IOM?"
- Uses simplified crew (3 agents)
- Quick response with basic information

### Complex Query
User: "I need comprehensive information about work visa documentation, cultural integration, and employment opportunities for migrating from India to Germany"
- Uses full crew (6 agents)
- Detailed multi-faceted response
- Includes risk assessment and resource coordination

### Risk Detection
User: "Someone offered me a modeling job in Dubai with all expenses paid, no experience needed"
- Risk assessment tool detects trafficking keywords
- Provides safety warnings
- Suggests official verification channels

## Performance Considerations

### Crew Complexity Detection
The system automatically determines whether to use:
- **Simplified Crew** (3 agents): Basic queries, faster response
- **Full Crew** (6 agents): Complex queries, comprehensive response

### Rate Limiting
- Configurable RPM limits to respect Azure OpenAI quotas
- Execution timeout protection
- Memory management for conversation history

### Fallback Strategy
- Hybrid endpoint provides graceful degradation
- Falls back to original RAG system if CrewAI fails
- Error handling with user-friendly messages

## Development

### Adding New Agents
1. Define agent in `agents.py` with role, goal, and backstory
2. Add corresponding task in `tasks.py`
3. Update crew configuration in `crew.py`
4. Assign appropriate tools

### Creating New Tools
1. Inherit from `BaseTool` in `tools.py`
2. Define input schema with Pydantic
3. Implement `_run()` method
4. Add to `get_migration_tools()` function
5. Assign to relevant agents

### Testing
Run the test suite:
```bash
python test_crew_ai.py
```

Tests cover:
- Basic CrewAI functionality
- Tool integration
- Complexity detection
- Configuration validation

## Best Practices

1. **Agent Specialization**: Keep agents focused on their specific domain
2. **Tool Efficiency**: Optimize tool queries for performance
3. **Error Handling**: Implement graceful degradation
4. **Rate Limiting**: Respect API quotas and limits
5. **Memory Management**: Limit conversation history length
6. **Security**: Validate inputs and sanitize outputs

## Troubleshooting

### Common Issues

1. **Configuration Errors**
   - Verify all Azure OpenAI credentials
   - Check embedding model deployment names
   - Validate API versions

2. **Performance Issues**
   - Reduce agent iterations
   - Optimize tool queries
   - Implement caching where appropriate

3. **Memory Issues**
   - Limit conversation history
   - Use simplified crew for basic queries
   - Monitor agent execution time

4. **Tool Access Issues**
   - Verify Chroma database path
   - Check JSON knowledge base availability
   - Validate file permissions

### Monitoring

Enable verbose logging in development:
```python
crew = Crew(verbose=True, ...)
```

Monitor execution times and adjust timeouts as needed.