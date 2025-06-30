# load .env file and set environment variables

import os
from dotenv import load_dotenv
from pathlib import Path

# Načtení .env souboru
env_path = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=env_path)

# API klíče
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Databázové spojení
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db/dbname")

# Nastavení aplikace
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")