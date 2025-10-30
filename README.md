# Multi-Agent System with Visual Editor

This project is a multi-agent system built on FastAPI and React technologies, allowing users to visually create, manage and run complex workflows composed of AI agents.

## Key Features

-   **User Authentication:** User registration and login using JWT tokens.
-   **Agents and AI models management:** Users can create custom agents and connect them with various AI Models (you need your own API key for these AI models).
-   **Workflow Visual editor:** Drag-and-drop interface for building graphs, where nodes represent agents and edges define transitions between them.
-   **Chat Interface:** Interaction with agents and graphs throught chat.
-   **Analysis** Display statiscs about agent usage and graph execution history.

## Used technologies
**Backend:**
-   **Framework:** FastAPI
-   **Database:** PostgreSQL s SQLAlchemy (asynchronous)
-   **Migration:** Alembic
-   **AI & Agents:** LangChain, LangGraph
-   **Authentication:** JWT, Passlib, python-jose
-   **Real-time:** WebSockets
-   **Server:** Uvicorn

**Frontend:**
-   **Framework:** React s TypeScriptem
-   **Build Tool:** Vite
-   **Routing:** React Router
-   **State Management:** React Context
-   **Styling:** Pure CSS

**Infrastructure:**
-   **Containerization:** Docker, Docker Compose



## Project structure

```
agent-system/
├── backend/            # FastAPI app
│   ├── alembic/        # Database migration
│   ├── app/            # Main app logic
│   │   ├── db/         # Models, schemas, DB connection
│   │   ├── routers/    # API endpoints
│   │   ├── services/   # Business logic (authentication, LangGraph builder)
|   |   └── utils/tools # Tools for agents
│   └── requirements.txt
│
├── frontend/           # React application
│   ├── src/
│   │   ├── components/ # Components
|   |   ├── css/        # CSS styling
│   │   ├── pages/      # Pages of application
│   │   └── services/   # React Contexts for managing states
├── docker-compose.yml  # Docker configuration
└── README.md           # This file
```


## Installation and Setup

### Requirements

-   [Docker](https://www.docker.com/get-started) Docker Compose
-   [Git](https://git-scm.com/)
-   [Node.js](https://nodejs.org/) npm (for local frontend development)
-   [Python](https://www.python.org/) (for local backend development)


### 1. Run with Docker Compose (recommended)

This command will run backend, frontend and database in seperate containers.

```bash
docker-compose up --build
```

-   **Backend API** will be available at `http://localhost:8000`
-   **Frontend app** will be available at `http://localhost:5173`
-   **API documentation** (Swagger) will be available at `http://localhost:8000/docs`


### 4. Local Setup (without Dockeru)

#### Backend

1.  Navigate to the backend folder `backend`.
2.  Create and activate virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Na Windows: venv\Scripts\activate
    ```
3.  Install dependecies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the database (e.g., via Docker or locally).
5.  Apply database migration:
    ```bash
    alembic upgrade head
    ```
6.  Run FastApi server:
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

#### Frontend

1.  Navigate to the frontend folder `frontend`.
2.  Install dependecies:
    ```bash
    npm install
    ```
3.  Run development server:
    ```bash
    npm run dev
    ```

---

## Database migration (Alembic)

If you make changes to SQLAlchemy moodels (`backend/app/db/models.py`), you need to generate and apply a new migration.

1.  Generate migration file (run in folder `backend`):
    ```bash
    alembic revision --autogenerate -m "Popis změn"
    ```
2.  Apply migration on database:
    ```bash
    alembic upgrade head
    ```


