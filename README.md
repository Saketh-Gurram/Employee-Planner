# 🚀 ProjectPilot - AI-Powered Employee Planner

> Multi-Agent AI System for Project Analysis & Intelligent Team Recommendations

ProjectPilot is an intelligent project scoping and feasibility analysis platform that uses a multi-agent AI architecture to analyze project requirements and recommend the best-fit employees from your talent pool based on skill matching, availability, and cost optimization.

## ✨ Features

- **🤖 Multi-Agent AI System**: Four specialized AI agents working together:
  - **Intake Agent**: Analyzes project requirements and scope
  - **Technical Agent**: Recommends technology stack and architecture
  - **Estimation Agent**: Calculates timelines, costs, and team composition
  - **Summary Agent**: Generates executive summaries and recommendations

- **👥 Intelligent Employee Matching**: Advanced algorithm that matches employees to project roles based on:
  - Skill proficiency and relevance
  - Years of experience
  - Seniority level alignment
  - Hourly rate and budget constraints
  - Current availability percentage

- **📊 Comprehensive Analysis**: Detailed reports including:
  - Technical architecture recommendations
  - Team composition with specific roles
  - Cost breakdown and alternative scenarios
  - Timeline estimation with milestones
  - Risk assessment and mitigation strategies
  - Employee recommendations with match percentages

- **🎨 Modern UI**: Professional Next.js/React interface with:
  - Tab-based navigation
  - Real-time analysis status updates
  - Interactive employee filtering and sorting
  - Cards and table view options
  - Downloadable reports (PDF/Markdown)

- **💰 Cost-Effective**: Uses Google Gemini 2.0 Flash (~$0.01-0.05 per analysis)

## 🏗️ Architecture

```
employee_planner/
├── frontend/                    # Next.js/React Frontend
│   ├── app/                    # Next.js app directory
│   ├── components/             # React components
│   │   ├── AnalysisResults.tsx # Main results display
│   │   └── ProjectAnalyzer.tsx # Project input form
│   ├── .env.local              # Frontend environment variables
│   ├── package.json            # Node dependencies
│   └── next.config.js          # Next.js configuration
│
├── backend/                    # FastAPI Backend
│   ├── agents/                 # Multi-agent system
│   │   ├── intake_agent.py     # Project intake analysis
│   │   ├── technical_agent.py  # Technical recommendations
│   │   ├── estimation_agent.py # Cost & timeline estimation
│   │   ├── summary_agent.py    # Executive summary generation
│   │   ├── base_agent.py       # Base agent class
│   │   └── agent_orchestrator.py # Coordinates all agents
│   ├── api/                    # API routes
│   │   └── routes.py           # FastAPI endpoints
│   ├── utils/                  # Utilities
│   │   ├── csv_data_service.py # CSV data loading
│   │   ├── employee_matcher.py # Employee matching algorithm
│   │   └── logger.py           # Logging configuration
│   ├── main.py                 # FastAPI application entry
│   └── requirements.txt        # Python dependencies
│
├── data/                       # Data files
│   └── samples/
│       ├── sample_employees.csv           # 30 employees with rates & availability
│       ├── sample_employee_skills.csv     # Employee skills with proficiency
│       └── sample_historical_projects.csv # Historical project data
│
└── README.md                   # This file
```

## 🚦 Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 16+** and **npm** (for frontend)
- **Google API Key** for Gemini AI
- Basic knowledge of command line

## 📋 Installation & Setup

### 1. Clone/Download the Project

```bash
git clone https://github.com/Saketh-Gurram/Employee-Planner.git
cd employee_planner
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Create Backend Environment File

Create a `.env` file in the `backend/` directory:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

**To get a Google API Key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it in your `.env` file

### 3. Frontend Setup

#### Install Node Dependencies

```bash
cd frontend
npm install
```

#### Create Frontend Environment File

Create a `.env.local` file in the `frontend/` directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Environment
NODE_ENV=development
```

### 4. Verify Installation

**Check Python dependencies:**
```bash
cd backend
python -c "import fastapi, google.generativeai, uvicorn; print('✅ Backend dependencies installed')"
```

**Check Node dependencies:**
```bash
cd frontend
npm list next react react-dom
```

## 🚀 Running the Application

### Step 1: Start the Backend Server

Open a terminal and run:

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

You should see:
```
[OK] Loaded 8 projects and 30 employees from CSV
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Step 2: Start the Frontend Server

Open a **new terminal** and run:

```bash
cd frontend
npm run dev
```

You should see:
```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
✓ Ready in 2.3s
```

**Note:** The frontend may run on port 3000, 3001, or 3002 depending on availability.

## 🌐 Accessing the Application

- **Frontend UI**: http://localhost:3000 (or the port shown in your terminal)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc (ReDoc)

## 📖 Usage Guide

### 1. Open the Application

Navigate to http://localhost:3000 in your web browser

### 2. Enter Project Description

In the text area, describe your project in detail. Include:
- **Application type** (web app, mobile app, desktop, etc.)
- **Key features and functionality**
- **Technical requirements or preferences**
- **Target users or market**
- **Special constraints** (budget, timeline, technology stack)

### 3. Analyze Project

Click the **"Analyze Project"** button and wait for the analysis to complete (typically 30-60 seconds).

### 4. Review Results

The analysis report includes multiple tabs:

#### 📊 Overview Tab
- Executive summary
- Project highlights (cost, timeline, team size)
- Complexity assessment

#### 💻 Technical Tab
- Recommended technology stack
- Architecture overview
- Integration requirements
- Security considerations

#### 👥 Team & Budget Tab
- **Available Talent Pool**: Preview of top matching employees
- **Team Composition**: Detailed role breakdowns with:
  - Role title and seniority level
  - Hours per week and duration
  - Hourly rate and total cost
  - Key responsibilities
  - **Recommended Employees** with match percentages
- **Cost Breakdown**: Development, infrastructure, tools, contingency
- **Timeline Breakdown**: All project phases

#### ⚠️ Risks Tab
- Major risks with impact and mitigation strategies
- Project dependencies
- Next steps and action items

#### 💡 Recommendations Tab
- Key recommendations prioritized by importance
- Implementation timelines
- Estimated effort

### 5. Filter and Sort Employees

In the Team & Budget tab, use the interactive filters:
- **Match Quality**: Filter by skill match percentage
- **Max Rate**: Set maximum hourly rate
- **Min Availability**: Filter by availability percentage
- **Sort By**: Match %, Rate, Availability, or Name
- **View Mode**: Toggle between Cards and Table view

### 6. Download Reports

Click the **"Download PDF"** or **"Download Markdown"** buttons at the top to export the complete analysis.

## 🎯 Example Project Descriptions

### Web Application
```
Build a SaaS project management platform using React and Next.js for the frontend,
with a FastAPI Python backend. Features include user authentication, project boards
with drag-and-drop task management, real-time collaboration, team chat, file uploads,
and analytics dashboard. Integrate with Stripe for billing and support both web and
mobile responsive design.
```

### Mobile App
```
Develop a cross-platform fitness tracking mobile app using React Native with features
like workout logging, progress tracking with charts, social sharing, integration with
wearable devices (Fitbit, Apple Watch, Garmin), AI-powered workout recommendations,
meal planning, and community challenges. Need both iOS and Android support.
```

### AI/ML Project
```
Create a machine learning platform for predictive maintenance in manufacturing using
Python, TensorFlow, and Apache Spark for real-time sensor data processing. Features
include anomaly detection, failure prediction models, automated alert systems,
historical data analysis dashboard, and integration with existing SCADA systems.
```

### Enterprise Application
```
Build an enterprise CRM system with advanced features including lead management,
sales pipeline visualization, email integration, automated workflows, reporting
and analytics, multi-tenant architecture, and SSO authentication. Technology
stack should support high scalability and include both web and mobile interfaces.
```

## 🔧 API Endpoints

### Backend API (Port 8000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/v1/analyze` | POST | Start new project analysis |
| `/api/v1/analysis/{analysis_id}` | GET | Get analysis status/results |
| `/api/v1/employees` | GET | Get all available employees |
| `/docs` | GET | Swagger API documentation |
| `/redoc` | GET | ReDoc API documentation |

## 📝 Tech Stack

### Frontend
- **Framework**: Next.js 14 (React 18)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Heroicons
- **HTTP Client**: Axios
- **Notifications**: React Hot Toast

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.8+
- **AI/ML**: LangChain + Google Gemini 2.0 Flash
- **Data**: Pandas (CSV processing)
- **Server**: Uvicorn (ASGI)

### AI Architecture
- **Multi-Agent System**: 4 specialized agents
- **LLM**: Google Gemini 2.0 Flash Experimental
- **Prompt Engineering**: Structured JSON responses
- **Context Management**: Sequential agent orchestration



**Made with ❤️ using Next.js, FastAPI, Google Gemini AI, and modern web technologies**

**Architecture**: Multi-Agent AI System with Intelligent Employee Matching
