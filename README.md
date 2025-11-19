# CareAgents

A modern healthcare management platform powered by AI agents, built with Google's Agent Development Kit (ADK) and deployed on Google Cloud Run.

## Overview

CareAgents is an intelligent healthcare tool that streamlines patient care, appointment management, and medical record processing through AI-powered automation. The platform leverages Google's generative AI capabilities to provide smart healthcare assistance including prescription parsing, appointment scheduling, patient onboarding, and real-time doctor-patient chat.

## Key Features

- **AI-Powered Chat Agents**: Intelligent conversational interfaces for patients and doctors
- **Prescription Parser**: Automated extraction and processing of prescription information
- **Smart Appointment Scheduling**: AI-driven appointment booking and management
- **Patient Onboarding**: Streamlined patient registration with embedding-based search
- **Medical History Management**: Comprehensive tracking of patient medical records
- **Voice Chat Support**: Real-time voice interactions with AI agents
- **Doctor Portal**: Dedicated interface for healthcare providers

## Tech Stack

### Backend
- **Framework**: FastAPI with Python 3.10+
- **Database**: PostgreSQL with asyncpg
- **AI/ML**: Google Agent Development Kit (ADK), Google Generative AI
- **Infrastructure**: Google Cloud Platform (Cloud Run)
- **Additional Libraries**: LiteLLM, Redis, WebSockets

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Components**: Radix UI, Tailwind CSS
- **State Management**: React Hooks
- **Deployment**: Docker + Cloud Run

## Folder Structure

```
CareAgents/
├── backend/                    # FastAPI backend application
│   ├── agents/                # AI agent implementations
│   │   ├── adk_chat_agent.py         # Main chat agent
│   │   ├── adk_record_agent.py       # Medical record processing agent
│   │   ├── appointment_agent.py      # Appointment management agent
│   │   ├── doctor_chat_agent.py      # Doctor-specific chat agent
│   │   ├── patient_embedding_agent.py # Patient data embedding/search
│   │   ├── prescription_parser_agent.py # Prescription parsing agent
│   │   ├── adk_tools.py              # Shared agent tools
│   │   ├── config/                   # Agent configurations
│   │   ├── services/                 # Agent support services
│   │   └── tools/                    # Custom agent tools
│   ├── routes/                # API route handlers
│   │   ├── admin.py                  # Admin management
│   │   ├── ai_appointments.py        # AI appointment scheduling
│   │   ├── appointments.py           # Appointment CRUD
│   │   ├── chat.py                   # Chat endpoints
│   │   ├── doctor_chat.py            # Doctor chat endpoints
│   │   ├── doctors.py                # Doctor management
│   │   ├── files.py                  # File upload/download
│   │   ├── medical_history.py        # Medical records
│   │   ├── onboarding.py             # Patient onboarding
│   │   ├── patients.py               # Patient management
│   │   ├── prescription_parser.py    # Prescription processing
│   │   ├── users.py                  # User authentication
│   │   └── voice_chat.py             # Voice chat handling
│   ├── models/                # Database models
│   ├── services/              # Business logic services
│   ├── database/              # Database configurations
│   ├── main.py                # Application entry point
│   ├── main_agents.py         # Agent initialization
│   ├── pyproject.toml         # Python dependencies
│   ├── Dockerfile             # Backend containerization
│   └── deploy.sh              # Deployment script
├── frontend/                  # React frontend application
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API service layer
│   │   ├── contexts/          # React contexts
│   │   ├── firebase/          # Firebase configuration
│   │   ├── utils/             # Utility functions
│   │   ├── App.tsx            # Main application component
│   │   └── main.tsx           # Application entry point
│   ├── package.json           # Node dependencies
│   ├── vite.config.ts         # Vite configuration
│   ├── Dockerfile             # Frontend containerization
│   ├── nginx.conf             # Nginx configuration
│   └── deploy.sh              # Deployment script
└── LICENSE                    # MIT License

```

## Deployment

The application is deployed on **Google Cloud Run**, providing:
- Automatic scaling based on traffic
- Pay-per-use pricing model
- HTTPS endpoints with managed SSL
- Container-based deployment
- High availability and reliability

### Deployment Scripts

Both backend and frontend include `deploy.sh` scripts for streamlined deployment to Cloud Run.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Node.js 20 or higher
- PostgreSQL database
- Google Cloud Platform account
- Google ADK API credentials

### Backend Setup

```bash
cd backend
uv sync
cp .env.example .env
# Configure your environment variables
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
# Configure your environment variables
npm run dev
```

## Environment Variables

Refer to `.env.example` files in both `backend/` and `frontend/` directories for required configuration.

## AI Agents

The platform utilizes Google's Agent Development Kit (ADK) to power intelligent agents:

- **Chat Agent**: Natural language interaction for general inquiries
- **Record Agent**: Medical record analysis and management
- **Appointment Agent**: Intelligent scheduling and availability management
- **Prescription Parser**: OCR and NLP-based prescription digitization
- **Patient Embedding Agent**: Vector-based patient data search and matching
- **Doctor Chat Agent**: Specialized agent for doctor-patient communication

## Contributors

- **Manideep Kuntimaddi** - [@manideepk90](https://github.com/manideepk90)
- **Abhay Kamble** - [@abzsd](https://github.com/abzsd)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Google Agent Development Kit (ADK)](https://cloud.google.com/products/agent-builder)
- Deployed on [Google Cloud Run](https://cloud.google.com/run)
- UI components from [Radix UI](https://www.radix-ui.com/)

---

For questions or support, please open an issue on the GitHub repository.
