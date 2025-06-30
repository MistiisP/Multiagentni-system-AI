import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

# Přidáme cestu k projektu do sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import Base
from app.db.models import Agent, ModelOfAI
from app.config import DATABASE_URL

async def main():
    print("Vytvářím výchozí agenty...")
    
    # Vytvoření engine a session
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        # Ujistíme se, že tabulky existují
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Vytvoření session
    async with async_session() as session:
        # Kontrola, zda již existují modely AI
        gpt4_model = await session.get(ModelOfAI, 1)
        
        if not gpt4_model:
            # Vytvoření výchozích modelů AI
            gpt4_model = ModelOfAI(
                name="OpenAI GPT-4o",
                model_identifier="gpt-4o"
            )
            session.add(gpt4_model)
            await session.commit()
            await session.refresh(gpt4_model)
            
            gpt35_model = ModelOfAI(
                name="OpenAI GPT-3.5-turbo",
                model_identifier="gpt-3.5-turbo"
            )
            session.add(gpt35_model)
        
        # Vytvoření výchozích agentů
        agents_data = [
            {
                "name": "Racionální asistent",
                "prompt": "Jsi racionální asistent, který vždy odpovídá logicky a věcně. "
                          "Tvým cílem je poskytnout jasné, fakticky správné informace. "
                          "Vyhýbáš se emocím a subjektivním hodnocením. "
                          "Když si nejsi jistý, přiznej to.",
                "model_id": gpt4_model.id
            },
            {
                "name": "Kreativní asistent",
                "prompt": "Jsi kreativní asistent se schopností generovat originální nápady. "
                          "Tvým cílem je přicházet s netradičními řešeními a pohledy. "
                          "Neboj se uvažovat mimo zaběhnuté koleje. "
                          "Využívej metafory, analogie a příklady pro ilustraci svých myšlenek.",
                "model_id": gpt4_model.id
            },
            {
                "name": "Kritický analytik",
                "prompt": "Jsi kritický analytik, který zkoumá problémy z různých úhlů. "
                          "Tvým cílem je identifikovat slabá místa v argumentaci a najít alternativní vysvětlení. "
                          "Vždy hledej protiargumenty k předkládaným tvrzením. "
                          "Používej logickou dedukci a poukazuj na předpoklady v tvrzeních.",
                "model_id": gpt4_model.id
            },
            {
                "name": "Empatický poradce",
                "prompt": "Jsi empatický poradce, který se snaží porozumět emocím a potřebám uživatele. "
                          "Tvým cílem je vytvořit bezpečný prostor pro sdílení a poskytovat podporu. "
                          "Používej reflektivní naslouchání a validaci pocitů. "
                          "Dávej návrhy, které respektují individuální situaci uživatele.",
                "model_id": gpt4_model.id
            }
        ]
        
        for agent_data in agents_data:
            # Kontrola, zda agent již existuje
            existing_agent = await session.execute(
                "SELECT id FROM agents WHERE name = :name",
                {"name": agent_data["name"]}
            )
            result = existing_agent.scalar_one_or_none()
            
            if not result:
                agent = Agent(
                    name=agent_data["name"],
                    prompt=agent_data["prompt"],
                    model_ai_id=agent_data["model_id"]
                )
                session.add(agent)
        
        await session.commit()
    
    print("Výchozí agenti vytvořeni!")

if __name__ == "__main__":
    asyncio.run(main())