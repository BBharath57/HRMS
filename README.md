# HRMS — Agentic AI Assistant

An AI-assisted Human Resource Management System built with Streamlit, LangGraph, SQLAlchemy, and retrieval-augmented generation (RAG). It supports employee and admin workflows for onboarding, leave management, and HR policy questions.

## Features

- Employee onboarding workflow
- Leave request workflow
- Admin onboarding and leave-management workflows
- Intent routing and workflow orchestration with LangGraph
- HR policy question answering using a RAG pipeline
- SQLAlchemy persistence with PostgreSQL or a local SQLite fallback
- Email notifications through SMTP
- Docker and Docker Compose configuration for local development

## Technology Stack

- **UI:** Streamlit
- **Agent orchestration:** LangGraph
- **LLM / RAG:** LangChain, Groq, Google Gemini embeddings, Pinecone
- **Database:** SQLAlchemy with PostgreSQL or SQLite
- **Email:** SMTP
- **Containerization:** Docker and Docker Compose

## Repository Layout

The current repository is being organized incrementally. The main entry point and modules currently include:

```text
HRMS/
├── ui/
│   └── main.py                 # Streamlit application entry point
├── hr_graph.py                 # LangGraph workflow orchestration
├── router_node.py              # Intent routing
├── onboarding_node.py          # Employee onboarding workflow
├── leave_node.py               # Employee leave workflow
├── admin_onboarding_node.py    # Admin onboarding workflow
├── admin_leave_node.py         # Admin leave workflow
├── hr_rag_node.py              # HR knowledge / RAG workflow
├── state.py                    # Shared graph state
├── db.py                       # SQLAlchemy database setup
├── models.py                   # Database models
├── email_service.py            # Email notifications
├── rag_pipeline.py             # Vector retrieval and LLM setup
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Prerequisites

- Python 3.11 (the Dockerfile uses Python 3.11)
- Git
- API credentials for the integrations you intend to use
- Docker Desktop (optional)

## Local Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/BBharath57/HRMS.git
   cd HRMS
   ```

2. Create and activate a virtual environment.

   **Windows PowerShell**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Create a local `.env` file from `.env.example` and fill in the values needed by the integrations you use. Never commit real credentials.

## Environment Variables

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Optional SQLAlchemy database URL. If unset, the current database module uses local SQLite at `./hrms.db`. |
| `GEMINI_API_KEY` | Google Gemini API key for embeddings |
| `GROQ_API_KEY` | Groq API key for the chat model |
| `PINECONE_API_KEY` | Pinecone credentials, if required by your Pinecone environment |
| `SENDER_EMAIL` | Sender address for SMTP notifications |
| `SENDER_PASSWORD` | SMTP/Gmail app password; keep secret |

The code may require additional configuration depending on the chosen database and external services. Review the relevant modules before deployment.

## Run the Application

From the repository root, run:

```bash
streamlit run ui/main.py
```

Streamlit normally opens the app in your browser at `http://localhost:8501`.

## Docker

The repository includes a `Dockerfile` and `docker-compose.yml`. Review and replace all development-only passwords in the Compose configuration before using it outside a local environment.

Build the application image:

```bash
docker build -t hrms .
```

Start the configured services:

```bash
docker compose up --build
```

## Database and Maintenance Scripts

The repository contains database setup and maintenance scripts. Inspect a script before running it, especially scripts that reset tables or delete/recreate a vector index. Back up data before any destructive operation.

## Security Notes

- Never commit `.env`, API keys, SMTP passwords, or database credentials.
- Use strong, unique credentials for admin accounts and databases.
- Replace development-only credentials in `docker-compose.yml` before exposing services.
- If a real credential was ever committed to Git history, rotate it; removing it from the current file alone does not invalidate it.

## Status

This README documents the current repository at a high level. Confirm the setup steps and all workflows in a local environment before deploying.
