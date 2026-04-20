# Finvexis AI

Finvexis AI is a full-stack intelligence platform that combines Business, Finance, and Sales/HR workflows in a single product. The project includes a React frontend and a FastAPI backend with domain-specific agent and analysis modules.

## Executive Summary

Finvexis AI is built to help teams move from raw operational data to actionable decisions. Instead of running disconnected tools across departments, the platform centralizes business strategy workflows, finance intelligence, and sales/hr assistance in one interface.

The application follows a modular design:
- A React frontend for user interaction and report consumption.
- A FastAPI backend for orchestration, domain logic, and agent execution.
- Domain-isolated modules so each function can evolve independently without breaking the entire system.

## Project Overview

Finvexis AI is designed to:
- Centralize multi-domain intelligence workflows.
- Provide an executive-facing UI for analysis and reporting.
- Expose backend APIs for business strategy, finance automation, and sales/hr tooling.

The system is organized into:
- `Frontend`: React + Vite application.
- `backend`: FastAPI service and domain modules.
- Root scripts for running frontend and backend together.

## Key Features

- Unified multi-domain intelligence across Business, Finance, and Sales/HR.
- Modular backend routes and agents for domain-specific processing.
- Frontend workspace architecture for reports, analysis, and guided workflows.
- Shared design token system for consistent, maintainable UI styling.
- Local-first development setup with independent frontend/backend runtime control.
- Extensible structure that supports adding new agents, tools, and routes.

## Repository Structure

```text
Finvexis/
├── Frontend/                    # React application (UI, pages, components)
│   ├── components/              # Reusable UI and feature components
│   ├── pages/                   # Route-level pages
│   ├── hooks/                   # React hooks
│   ├── lib/                     # Frontend domain helpers and mock data
│   ├── App.tsx                  # Top-level app routes and providers
│   ├── index.css                # Global design system tokens and styles
│   └── main.tsx                 # Frontend entry point
├── backend/                     # FastAPI backend and domain engines
│   ├── routes/                  # API route modules (business, finance, sales)
│   ├── Business/                # Business intelligence agents and orchestration
│   ├── finance/                 # Finance agents, engines, and utilities
│   ├── Sales_HR/                # Sales and HR tools, parser, and utilities
│   └── main.py                  # Backend entry point
├── package.json                 # Root scripts to run full stack
└── README.md                    # This file
```

## Architecture Overview

### Frontend Layer

The frontend handles:
- User navigation and workspace rendering.
- Form/input interactions and API trigger points.
- Presentation of analysis outputs from backend services.

Key files:
- `Frontend/main.tsx`: application bootstrap.
- `Frontend/App.tsx`: provider setup and route configuration.
- `Frontend/pages/Index.tsx`: main landing and primary experience flow.

### Backend Layer

The backend handles:
- Request validation and API routing.
- Domain orchestration for business, finance, and sales/hr modules.
- Execution of domain agents and utility pipelines.

Key files:
- `backend/main.py`: FastAPI app creation, middleware, and router registration.
- `backend/routes/*.py`: domain API endpoints.
- Domain modules in `backend/Business`, `backend/finance`, and `backend/Sales_HR`.

### End-to-End Request Flow

1. User action is triggered from frontend workspace components.
2. Frontend calls corresponding backend route.
3. Route delegates processing to domain orchestrator/agent modules.
4. Domain module computes response and returns structured output.
5. Frontend renders the result in cards, summaries, or analysis sections.

## Tech Stack

### Frontend
- React
- TypeScript
- Vite
- Tailwind-style tokenized CSS system
- React Router
- TanStack Query

### Backend
- Python 3.10
- FastAPI
- Uvicorn
- Modular domain orchestration for:
  - Business intelligence
  - Finance workflows
  - Sales and HR operations

## Domain Modules

### Business Intelligence
- Strategy-oriented processing and orchestration.
- Agent modules for forecasting, KPI interpretation, and business planning support.

### Finance
- Invoice, budgeting, auditing, and vendor intelligence workflows.
- Engine-based structure for parsing, profiling, alerts, and finance narratives.

### Sales and HR
- Tools for resume intelligence, job description analysis, lead/sales assistance, and policy support.
- Utility modules for document handling and classification.

## Prerequisites

- Node.js and npm
- Python 3.10
- Virtual environment located at `./venv` with backend dependencies installed
- Optional `.env` file at repository root for backend configuration

## Installation

### 1) Install root dependencies

```bash
npm install
```

### 2) Install frontend dependencies

```bash
cd Frontend
npm install
```

### 3) Ensure backend environment exists

Backend is expected to run using:

```bash
./venv/bin/python3.10
```

Install backend dependencies in that environment if needed.

## Running the Project

From repository root:

### Run frontend only

```bash
npm run dev:frontend
```

### Run backend only

```bash
npm run dev:backend
```

### Run full stack concurrently

```bash
npm run dev
```

## Backend API

Base backend app is served from `backend/main.py`.

Integrated route groups:
- `business` domain endpoints
- `finance` domain endpoints
- `sales` domain endpoints

Health/root response:
- `GET /` returns a welcome message.

## Configuration Notes

- Backend reads environment variables from the root `.env` file.
- Frontend dev server proxies API calls to backend (`http://127.0.0.1:8000`) via Vite config.
- Keep secrets and environment-specific keys out of source files.

## Frontend Notes

- Main app shell and routes are defined in `Frontend/App.tsx`.
- Landing experience is implemented in `Frontend/pages/Index.tsx` and `Frontend/components/landing`.
- Global theme tokens and shared styles are defined in `Frontend/index.css`.

## Development Guidelines

- Keep feature logic domain-scoped under `backend/Business`, `backend/finance`, and `backend/Sales_HR`.
- Keep UI concerns in `Frontend/components` and page composition in `Frontend/pages`.
- Prefer reusable components and shared design tokens over one-off styling.
- Keep route modules in `backend/routes` thin and delegate logic to domain modules.

## Troubleshooting

- If backend does not start, verify `./venv/bin/python3.10` exists and dependencies are installed.
- If frontend fails, reinstall frontend dependencies in `Frontend`.
- If API requests fail from frontend, verify backend is running on `http://127.0.0.1:8000` and Vite proxy is active.

## Conclusion

Finvexis AI provides a solid foundation for an integrated intelligence product where multiple business functions can operate from one coherent system. Its layered architecture, domain separation, and extensible module organization make it suitable for rapid iteration now and scalable growth later.

As the project evolves, the current structure supports:
- Adding new domain agents with minimal coupling.
- Expanding APIs without disrupting existing workflows.
- Improving frontend experiences while preserving design consistency.

