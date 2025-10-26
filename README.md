# Multi-Agent System s vizuálním editorem

Tento projekt je multi-agentní systém postavený na technologiích FastAPI a React, který umožňuje uživatelům vizuálně vytvářet, spravovat a spouštět komplexní workflow (grafy) složené z AI agentů.

## Klíčové vlastnosti

-   **Uživatelská autentizace:** Registrace a přihlašování uživatelů pomocí JWT tokenů.
-   **Správa agentů a AI modelů:** Uživatelé si mohou vytvářet vlastní agenty a propojovat je s různými AI modely (např. OpenAI).
-   **Vizuální editor workflow:** Drag-and-drop rozhraní pro sestavování grafů, kde uzly reprezentují agenty a hrany definují přechody mezi nimi.
-   **Chatovací rozhraní:** Interakce s agenty a grafy prostřednictvím chatu.
-   **Analytika:** Zobrazení statistik o využití agentů a historie spuštění grafů.


## Použité technologie
**Backend:**
-   **Framework:** FastAPI
-   **Databáze:** PostgreSQL s SQLAlchemy (asynchronní)
-   **Migrace:** Alembic
-   **AI & Agenti:** LangChain, LangGraph
-   **Autentizace:** JWT, Passlib, python-jose
-   **Real-time:** WebSockets
-   **Server:** Uvicorn

**Frontend:**
-   **Framework:** React s TypeScriptem
-   **Build Tool:** Vite
-   **Routing:** React Router
-   **Stavové kontejnery:** React Context
-   **Stylování:** Čisté CSS

**Infrastruktura:**
-   **Kontejnerizace:** Docker, Docker Compose



## Struktura projektu

```
agent-system/
├── backend/            # FastAPI aplikace
│   ├── alembic/        # Databázové migrace
│   ├── app/            # Hlavní logika aplikace
│   │   ├── db/         # Modely, schémata, připojení k DB
│   │   ├── routers/    # API endpointy
│   │   ├── services/   # Business logika (autentizace, LangGraph builder)
|   |   └── utils/tools # Logika pro agenty s nástroji
│   ├── .env            # Konfigurace a klíče (lokální)
│   └── requirements.txt
│
├── frontend/           # React aplikace
│   ├── src/
│   │   ├── components/ # Komponenty
|   |   ├── css/        # CSS stylování
│   │   ├── pages/      # Stránky aplikace
│   │   └── services/   # React Contexty pro správu stavu
│   └── .env            # Konfigurace pro frontend
│
├── docker-compose.yml  # Konfigurace pro spuštění projektu v Dockeru
└── README.md           # Tento soubor
```







## Instalace a spuštění

### Požadavky

-   [Docker](https://www.docker.com/get-started) a Docker Compose
-   [Git](https://git-scm.com/)
-   [Node.js](https://nodejs.org/) a npm (pro případný lokální vývoj frontendu)
-   [Python](https://www.python.org/) (pro případný lokální vývoj backendu)

### 1. Klonování repozitáře

```bash
git clone <URL_VAŠEHO_REPOZITÁŘE>
cd agent-system
```

### 2. Konfigurace prostředí

Projekt vyžaduje `.env` soubory pro backend i frontend.

**Backend:**
Vytvoř soubor `backend/.env` a vlož do něj potřebné klíče:
```env
# backend/.env
DATABASE_URL="postgresql+asyncpg://test_user:test123@db:5432/MAS_system_db"
SECRET_KEY="<VAŠ_TAJNÝ_KLÍČ_PRO_JWT>"
OPENAI_API_KEY="<VAŠ_OPENAI_API_KLÍČ>"
TAVILY_API_KEY="<VAŠ_TAVILY_API_KLÍČ>"
# ... další klíče
```

**Frontend:**
Vytvoř soubor `frontend/.env` a nastav URL backendu:
```env
# frontend/.env
VITE_API_URL=http://127.0.0.1:8000
```

### 3. Spuštění pomocí Docker Compose (doporučeno)

Tento příkaz spustí backend, frontend i databázi v oddělených kontejnerech.

```bash
docker-compose up --build
```

-   **Backend API** bude dostupné na `http://localhost:8000`
-   **Frontend aplikace** bude dostupná na `http://localhost:5173`
-   **API dokumentace** (Swagger) je na `http://localhost:8000/docs`



### 4. Lokální spuštění (bez Dockeru)

#### Backend

1.  Přejdi do složky `backend`.
2.  Vytvoř a aktivuj virtuální prostředí:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Na Windows: venv\Scripts\activate
    ```
3.  Nainstaluj závislosti:
    ```bash
    pip install -r requirements.txt
    ```
4.  Spusť databázi (např. přes Docker nebo lokálně).
5.  Aplikuj databázové migrace:
    ```bash
    alembic upgrade head
    ```
6.  Spusť FastAPI server:
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

#### Frontend

1.  Přejdi do složky `frontend`.
2.  Nainstaluj závislosti:
    ```bash
    npm install
    ```
3.  Spusť vývojový server:
    ```bash
    npm run dev
    ```

---

## Databázové migrace (Alembic)

Pokud provedete změny v SQLAlchemy modelech (`backend/app/db/models.py`), je potřeba vygenerovat a aplikovat novou migraci.

1.  Vygeneruj migrační soubor (spusť ve složce `backend`):
    ```bash
    alembic revision --autogenerate -m "Popis změn"
    ```
2.  Aplikuj migraci na databázi:
    ```bash
    alembic upgrade head
    ```


    
********************************************************************
- postgresql+asyncpg://test_user:test123@localhost:5433/MAS_system_db
- test_user, password "test123", superuser
- create new user 
ALTER USER postgres WITH PASSWORD 'postgres';
ALTER USER test_user WITH PASSWORD 'test123';

SHOW port;
