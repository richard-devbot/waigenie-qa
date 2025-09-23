# SDET-GENIE: AI-Powered QA Automation Framework

![SDET-GENIE Architecture](https://github.com/user-attachments/assets/87ecb2a9-0638-4dee-b630-74aed4e95326)

## 🚀 Project Overview

SDET-GENIE is a cutting-edge, AI-powered Quality Assurance (QA) automation framework that revolutionizes the software testing process. This is the migrated version from Streamlit to a modern FastAPI + Next.js architecture while maintaining 100% feature parity.

The framework integrates five powerful AI agents working in sequence:

1. **User Story Enhancement Agent** - Transforms rough ideas into detailed JIRA-style user stories
2. **Manual Test Case Agent** - Converts enhanced user stories into comprehensive test cases
3. **Gherkin Scenario Agent** - Transforms test cases into structured Gherkin feature files
4. **Browser Agent** - Executes Gherkin scenarios in real browsers and captures interaction data
5. **Code Generation Agent** - Produces ready-to-run automation code in multiple frameworks

## 🏗️ Architecture

### Backend (FastAPI)
- **Language**: Python 3.11+
- **Framework**: FastAPI with async support
- **API Documentation**: Auto-generated OpenAPI/Swagger UI
- **Database**: SQLite (optional, for task persistence)
- **Task Management**: Async task handling with background processing
- **Browser Automation**: Playwright integration via browser-use library

### Frontend (Next.js 14)
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom components with shadcn/ui patterns
- **State Management**: React Server Components + Client Components
- **API Integration**: Axios for backend communication

## 📁 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app initialization
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── settings.py         # Environment variables, configurations
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── request_models.py   # Pydantic request models
│   │   │   └── response_models.py  # Pydantic response models
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── story_service.py    # Story enhancement logic
│   │   │   ├── test_service.py     # Manual test generation
│   │   │   ├── gherkin_service.py  # Gherkin generation
│   │   │   ├── executor_service.py # Browser execution
│   │   │   └── code_service.py     # Code generation
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   └── agno_agents.py      # Migrated from original agents.py
│   │   ├── prompts/
│   │   │   ├── __init__.py
│   │   │   └── [copy all prompt files as-is]
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── file_handler.py
│   │   │   └── task_manager.py     # For async execution tracking
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── deps.py             # Dependencies
│   │       └── v1/
│   │           ├── __init__.py
│   │           ├── story.py        # Story endpoints
│   │           ├── tests.py        # Test generation endpoints
│   │           ├── gherkin.py      # Gherkin endpoints
│   │           ├── execute.py      # Execution endpoints
│   │           └── code.py         # Code generation endpoints
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── layout.tsx              # Root layout
│   │   ├── page.tsx               # Home page
│   │   ├── globals.css            # Global styles
│   │   ├── dashboard/
│   │   │   ├── layout.tsx         # Dashboard layout
│   │   │   ├── page.tsx           # Dashboard home
│   │   │   ├── enhance/
│   │   │   │   └── page.tsx       # Story enhancement
│   │   │   ├── tests/
│   │   │   │   └── page.tsx       # Manual tests
│   │   │   ├── gherkin/
│   │   │   │   └── page.tsx       # Gherkin generation
│   │   │   ├── execute/
│   │   │   │   └── page.tsx       # Execution page
│   │   │   └── code/
│   │   │       └── page.tsx       # Code generation
│   │   └── api/                   # Server actions (optional)
│   ├── components/
│   │   ├── ui/                    # shadcn/ui components
│   │   ├── dashboard/
│   │   │   ├── StoryEnhancer.tsx
│   │   │   ├── TestGenerator.tsx
│   │   │   ├── GherkinGenerator.tsx
│   │   │   ├── ExecutionPanel.tsx
│   │   │   ├── CodeGenerator.tsx
│   │   │   └── ResultsViewer.tsx
│   │   ├── common/
│   │   │   ├── FileUpload.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── ErrorBoundary.tsx
│   │   │   └── ProgressTracker.tsx
│   │   └── layout/
│   │       ├── Sidebar.tsx
│   │       ├── Header.tsx
│   │       └── Navigation.tsx
│   ├── lib/
│   │   ├── api.ts                 # API client
│   │   ├── utils.ts               # Utility functions
│   │   ├── constants.ts           # App constants
│   │   └── types.ts               # TypeScript types
│   ├── hooks/
│   │   ├── useApi.ts              # API hooks
│   │   ├── usePolling.ts          # Polling for execution status
│   │   └── useLocalStorage.ts     # Local state persistence
│   ├── contexts/
│   │   └── AppContext.tsx         # Global state management
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.js
│   ├── components.json            # shadcn/ui config
│   └── next.config.js
├── docker-compose.yml             # Docker Compose for local development
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Using Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd sdet-genie
   ```

2. **Set up environment variables:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env and add your API keys
   ```

3. **Start the services:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development

#### Backend Setup:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install
cp .env.example .env
# Edit .env with your API keys
uvicorn app.main:app --reload
```

#### Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the `backend` directory based on `.env.example`:

```env
# LLM API Keys (at least one required)
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GROQ_API_KEY=your_groq_api_key

# Optional Jira Configuration
JIRA_SERVER_URL=
JIRA_USERNAME=
JIRA_TOKEN=

# Backend Configuration
BACKEND_HOST=localhost
BACKEND_PORT=8000
DEBUG=True
```

##  API Endpoints

### Story Enhancement
- `POST /api/v1/story/enhance` - Enhance user story

### Manual Test Generation
- `POST /api/v1/tests/generate` - Generate manual test cases

### Gherkin Generation
- `POST /api/v1/gherkin/generate` - Generate Gherkin scenarios

### Execution Management
- `POST /api/v1/execute/start` - Start test execution
- `GET /api/v1/execute/status/{task_id}` - Get execution status
- `GET /api/v1/execute/results/{task_id}` - Get execution results

### Code Generation
- `POST /api/v1/code/generate` - Generate automation code

### File Management
- `POST /api/v1/files/upload` - Upload files
- `GET /api/v1/files/download/{file_id}` - Download files

## 🎨 UI Features

- **Modern Dashboard**: Intuitive navigation and workflow
- **Step-by-Step Process**: Clear progression from story to code
- **Real-time Updates**: Live status during execution
- **Comprehensive Results**: Detailed execution analysis
- **Debugging Tools**: Recordings, screenshots, network traces
- **Multi-framework Support**: Generate code for various testing frameworks

## 🛠️ Development

### Backend Development
The backend follows a clean architecture pattern with clear separation of concerns:
- **Models**: Pydantic models for request/response validation
- **Services**: Business logic implementation
- **API**: FastAPI routers and endpoints
- **Agents**: AI agent implementations
- **Utils**: Helper functions and utilities

### Frontend Development
The frontend uses Next.js 14 with App Router:
- **TypeScript**: Full type safety
- **Tailwind CSS**: Utility-first styling
- **React Hooks**: State and side effect management
- **API Client**: Centralized API communication
- **Responsive Design**: Works on all device sizes

## 🧪 Testing

### Backend Testing
```bash
cd backend
# Run unit tests
python -m pytest tests/unit

# Run integration tests
python -m pytest tests/integration

# Run end-to-end tests
python -m pytest tests/e2e
```

### Frontend Testing
```bash
cd frontend
# Run component tests
npm run test

# Run end-to-end tests
npm run test:e2e
```

## 📚 Documentation

- **API Documentation**: Auto-generated at `/docs` and `/redoc`
- **Code Documentation**: Inline comments and docstrings
- **Architecture Diagrams**: Visual representations of system design
- **User Guides**: Step-by-step usage instructions

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0)

## 🌈 Acknowledgments

- Powered by cutting-edge AI technologies
- Enhanced with the browser-use library for advanced browser automation capabilities
- Inspired by the challenges in modern software quality assurance

## 🆘 Support

- Open a GitHub Issue for bug reports or feature requests
- Check existing issues and discussions
- Join our community Discord (link coming soon)

---
**Made with ❤️ by the WaiGenie Team**
```

## 代码修改建议
```
# Full-Stack SDET (Software Development Engineer in Test)

This project implements a comprehensive testing solution with AI-powered browser automation capabilities, enhanced with parallel execution features from a friend's advanced implementation.

## Features

### Enhanced Browser Automation
- **Parallel Execution**: Run multiple Gherkin scenarios simultaneously using tab management
- **Element Tracking**: Comprehensive element attribute capture for automation code generation
- **Multi-Framework Support**: Export test scripts to Selenium, Playwright, and Cypress
- **Visual Feedback**: Screenshots, GIFs, and video recordings of test executions

### Advanced Features from Friend's Implementation
- **Enhanced BrowserManager**: Improved session management with agent isolation
- **Parallel Action Execution**: Execute compatible actions in parallel for faster test execution
- **Improved Target Assignment**: Better tab management with ownership tracking
- **Enhanced Watchdogs**: Custom action and DOM watchdogs with parallel processing capabilities

## Project Structure

```
full-stack-sdet/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── browser/
│   │   │   ├── watchdog/
│   │   │   ├── agent_browser_profile.py
│   │   │   ├── agent_browser_session.py
│   │   │   └── browser_manager.py
│   │   ├── services/
│   │   │   └── browser_execution_service.py
│   │   └── utils/
│   └── requirements.txt
├── frontend/
├── tests/
│   └── test_parallel_execution_upgraded.py
├── demo_parallel_execution_upgraded.py
└── README.md
```

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd full-stack-sdet
   ```

2. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

## Usage

### Running the Demo
```bash
python demo_parallel_execution_upgraded.py
```

### Running Tests
```bash
cd tests
python -m pytest test_parallel_execution_upgraded.py
```

## Key Enhancements

### 1. Parallel Execution with Tab Management
The upgraded implementation allows running multiple browser automation scenarios in parallel within the same browser instance using separate tabs, significantly reducing resource consumption while maintaining isolation between test scenarios.

### 2. Enhanced Element Tracking
Comprehensive element attribute capture including:
- Standard attributes (id, class, name, etc.)
- Accessibility information
- Position and bounds data
- Computed styles
- Framework-specific selectors

### 3. Multi-Framework Export
Generate test scripts for popular automation frameworks:
- **Selenium**: Python-based web testing framework
- **Playwright**: Cross-browser automation library
- **Cypress**: JavaScript end-to-end testing framework

### 4. Advanced Action Processing
- **Parallel Action Execution**: Execute compatible actions simultaneously
- **Action Grouping**: Group consecutive actions that can be executed in parallel
- **DOM Synchronization**: Verify element indexes are still valid after actions

## API Endpoints

### Browser Execution Service
- `POST /execute/browser-test`: Execute a single browser test
- `POST /execute/parallel-browser-tests`: Execute multiple browser tests in parallel

## Configuration

The service can be configured through environment variables:
- `BROWSER_USE_API_KEY`: API key for the selected LLM provider
- `BROWSER_USE_MODEL`: Specific model to use (default: gemini-2.0-flash)
- `BROWSER_USE_HEADLESS`: Run browser in headless mode (default: false)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the [browser-use](https://github.com/browser-use/browser-use) library
- Enhanced with advanced features from a friend's implementation
