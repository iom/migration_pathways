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
├── docker-compose.yml      # Docker container orchestration
├── init-db.sql             # Database initialization script
└── .env.example            # Environment variables template
```

## Prerequisites

- Docker and Docker Compose
- Git
- Azure OpenAI API access (for production)

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/migration_pathways.git
   cd migration_pathways
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env file with your settings
   ```

3. **Start the application with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost:8510

## Development Environment

### Backend Development

```bash
cd backend
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt

# Set up PostgreSQL locally or use Docker:
docker run --name postgres -e POSTGRES_PASSWORD=your_secure_password -e POSTGRES_USER=iom_uc2_user -e POSTGRES_DB=iom_uc2 -p 5432:5432 -d postgres:14-alpine

# Run the backend server:
python main.py
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Database Setup

The PostgreSQL database is automatically initialized with the required tables when using Docker Compose. For manual setup, see the [backend README](backend/README.md).

## CI/CD Pipeline

This project utilizes GitHub Actions for Continuous Integration and Deployment:

- **CI Pipeline:** Runs on PR and pushes to main/dev branches
  - Lints and tests frontend code
  - Lints and tests backend code
  - Builds Docker images

- **CD Pipeline:** Runs on pushes to main branch and tags
  - Builds and pushes Docker images to GitHub Container Registry
  - Deploys to staging/production environments

## Environment Variables

See `.env.example` for the required environment variables.

## Docker Deployment

The application can be deployed using Docker Compose:

```bash
# Production deployment
docker-compose -f docker-compose.yml up -d
```

