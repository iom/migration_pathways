# Migration Pathways – AI Chatbot for Safe and Informed Migration Decisions  

**A humane AI assistant providing verified migration information and personalized pathways**  

## 🌍 About  

The International Organization for Migration (IOM) is an intergovernmental organization that aims to promote humane and orderly migration for the benefit of all. This project presents an AI-powered solution to make migration **safer**, **smarter**, and **more informed**.  

Migration journeys often involve significant risks:  
⚠️ **Human Trafficking** - False employment promises leading to exploitation  
⚠️ **Smuggling Networks** - Dangerous crossings resulting in financial loss or worse  
⚠️ **Physical Violence** - Robbery, assault, or kidnapping during transit  

This chatbot addresses critical information gaps migrants face when deciding:  
- ✅ Ideal destination matching their profile  
- 📝 Legal pathways based on nationality/skills  
- 💼 Labor market realities  
- 🎓 Education opportunities  
- 🌐 Cultural integration  
- 💰 Cost/risk assessment  

## ✨ Key Features  

| Feature | Benefit |  
|---------|---------|  
| **Always Updated** | Verified information with official sources |  
| **Personalized Guidance** | Tailored to origin/destination/circumstances |  
| **Emotionally Intelligent** | Detects and responds to user's emotional state |  
| **Multilingual Support** | Accessible in native languages |  
| **Conversational UI** | No complex documents - just natural dialogue |  

## 🛠️ Technical Overview  

**AI Agentic System Architecture**:  
The application used an AI agentic system, powered by [CrewAI](https://docs.crewai.com/introduction), consists of a React frontend and a Python Flask backend with PostgreSQL database.

## 🤝 Contributing

> 🚧 This project is licensed under the MIT License. It is in active development. Contributions are welcome!

The system uses IOM-standard proposal structures and can be definitely adapted to other UN Humanitarian agencies (e.g., UNHCR, OCHA, UNICEF, WFP).

If you can contribute to the project, please follow these steps:
1. Fork the repo
2. Create a feature branch
3. Commit changes
4. Open a pull request



## Project Structure

```
migration_pathways/
├── .github/workflows/      # GitHub Actions CI/CD pipelines
├── backend/                # Flask API, AI model integration, database operations
├── frontend/               # React UI
├── migration-azure-docker-compose.yml      # Docker container orchestration
├── database-setup.sql             # Database initialization script
└── .env.example            # Environment variables template
```

## Prerequisites

- Docker and Docker Compose
- Git
- Azure OpenAI API access (for production)

## Project Overview

This is an AI-powered migration assistance chatbot built for the International Organization for Migration (IOM). It provides verified migration information and personalized pathways to help migrants make safer, informed decisions.

**Architecture**: Flask backend with React frontend, PostgreSQL database, and enhanced AI system combining RAG (Retrieval-Augmented Generation) with CrewAI multi-agent architecture using Azure OpenAI and Chroma vector database.

## Development Commands

### Backend Development
```bash
cd backend
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
python main.py  # Runs on port 80
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev     # Runs on port 8509
npm run build   # Production build
npm run lint    # ESLint
npm test        # Vitest tests
npm run test:ui # Vitest UI
```

### Testing
```bash
# Backend tests
cd backend
pytest

# CrewAI integration test
cd backend
python test_crew_ai.py

# Frontend tests
cd frontend
npm test
```

### Docker Development
```bash
# Full stack with Docker Compose
docker-compose -f migration-azure-docker-compose.yml up -d

# Individual services
docker build -t migration-backend ./backend
docker build -t migration-frontend ./frontend
```

## Architecture Details

### Backend (Flask)
- **Main entry**: `backend/main.py` - Flask app with authentication, admin routes, and user management
- **Chat systems**: 
  - `backend/chat_rag.py` - Original RAG implementation with Azure OpenAI and Chroma
  - `backend/chat_crew_ai.py` - Enhanced CrewAI multi-agent system
- **Database**: PostgreSQL with SQLAlchemy ORM, connection via `utility/db_config.py`
- **Authentication**: JWT tokens with httpOnly cookies, role-based access (users/admins)
- **CrewAI Agent System**:
  - **Agents**: `backend/crew_ai/agents.py` - 6 specialized migration agents
    - Migration Advisor: Primary pathway guidance
    - Risk Assessment: Safety and fraud detection
    - Documentation Specialist: Legal requirements and paperwork
    - Cultural Integration: Adaptation and community support
    - Employment Advisor: Job markets and skill recognition
    - Resource Coordinator: IOM contacts and NGO connections
  - **Tasks**: `backend/crew_ai/tasks.py` - Structured task definitions for agent coordination
  - **Tools**: `backend/crew_ai/tools.py` - Vector search, contact lookup, risk assessment tools
  - **Orchestration**: `backend/crew_ai/crew.py` - Crew management and execution logic
- **RAG Components**:
  - Vector store: Chroma database in `backend/chroma_store/`
  - Embeddings: Azure OpenAI embeddings for semantic search
  - Knowledge sources: Web scraped content + JSON knowledge base
  - Document processing: `utility/embedder.py`, `utility/scraper_and_embedder.py`

### Frontend (React + Vite)
- **Framework**: React 19 with React Router DOM for navigation
- **Build tool**: Vite with SWC for fast compilation
- **Testing**: Vitest + React Testing Library + MSW for API mocking
- **Styling**: CSS modules with responsive design
- **Proxy**: Development proxy `/api` → `http://localhost:8510` (backend)

### Database Schema
- **users**: User accounts with authentication, preferences, session management
- **admins**: Admin accounts with elevated privileges
- Key fields: email, password (hashed), request_count, active status, security_questions

### Key Features
- **Enhanced Chat Interface**: 
  - `/api/chat` - Original RAG-based responses
  - `/api/chat/crew` - CrewAI multi-agent specialized responses
  - `/api/chat/hybrid` - Automatic fallback from CrewAI to RAG
- **Multi-Agent AI System**: 6 specialized agents working collaboratively
- **Intelligent Risk Assessment**: Automated detection of trafficking, fraud, and unsafe migration practices
- **Comprehensive Guidance**: Legal documentation, cultural integration, employment advice
- **Dynamic Resource Coordination**: Contextual IOM office and NGO recommendations
- **Admin Dashboard**: Content management, user administration, URL scraping
- **Authentication**: Secure login/logout with session management
- **Content Management**: Web scraping, document upload, knowledge base updates
- **Preferences**: User source/destination country settings for personalized responses

## Environment Variables

Required environment variables (see `.env.example`):
- `SECRET_KEY`: JWT signing key
- `DB_*`: PostgreSQL connection details
- `AZURE_OPENAI_*`: Azure OpenAI service credentials for chat model
- `AZURE_*_EMBED`: Azure OpenAI embedding service credentials
- `VITE_BACKEND_URL`: Frontend API endpoint

**CrewAI-specific variables**:
- `AZURE_EMBEDDING_MODEL`: Embedding model name (e.g., text-embedding-ada-002)
- `AZURE_OPENAI_ENDPOINT_EMBED`: Separate endpoint for embeddings (if different)
- `AZURE_OPENAI_API_KEY_EMBED`: API key for embedding service
- `AZURE_EMBEDDING_DEPLOYMENT_NAME`: Deployment name for embedding model
- `AZURE_OPENAI_API_VERSION_EMBED`: API version for embedding service

## Development Workflow

1. **Database Setup**: Run `database-setup.sql` to initialize PostgreSQL
2. **Environment**: Copy `.env.example` to `.env` and configure all Azure OpenAI endpoints
3. **Backend**: Install dependencies including CrewAI, start Flask server on port 80
4. **Frontend**: Install dependencies, start Vite dev server on port 8509
5. **CrewAI Testing**: Run `python test_crew_ai.py` to verify agent system
6. **Testing**: Run pytest (backend) and vitest (frontend) before commits

### CrewAI Development Notes
- **Agent Modifications**: Edit `backend/crew_ai/agents.py` to adjust agent roles and capabilities
- **Task Updates**: Modify `backend/crew_ai/tasks.py` to change agent coordination logic
- **Tool Enhancement**: Add new tools in `backend/crew_ai/tools.py` for expanded functionality
- **Configuration**: Adjust settings in `backend/crew_ai/config.py` for performance tuning
- **Testing Endpoints**:
  - GET `/api/chat/crew/status` - Check CrewAI system health
  - POST `/api/chat/crew/reset` - Reset user conversation history
  - POST `/api/chat/hybrid` - Use intelligent fallback system

## Common Issues

- **CORS**: Frontend dev server proxies API calls through Vite config
- **Database**: Ensure PostgreSQL is running and credentials are correct
- **Azure OpenAI**: Verify both chat and embedding endpoints are configured
- **Chroma**: Vector database persists in `backend/chroma_store/`
- **CrewAI Issues**:
  - **Rate Limits**: Azure OpenAI rate limiting may affect agent execution
  - **Memory Usage**: Multiple agents can consume significant memory
  - **Timeout**: Complex queries may exceed execution time limits
  - **Dependencies**: Ensure all CrewAI and LangChain packages are compatible versions
  - **Tools Access**: Verify tools have access to vector store and JSON knowledge base

## Deployment

- **Production**: Uses `migration-azure-docker-compose.yml` with nginx proxy
- **Services**: nginx-proxy (port 80) → frontend → backend → PostgreSQL
- **CI/CD**: GitHub Actions workflow in `.github/workflows/`