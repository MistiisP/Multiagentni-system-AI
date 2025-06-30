import re
import os
import httpx
import requests
from typing import Dict, Any, List, Tuple
from .db.schemas import AgentState

# Load prompts from files
with open("prompts/query_prompt.txt", "r", encoding="utf-8") as f:
    QUERY_PROMPT = f.read()

with open("prompts/research_prompt.txt", "r", encoding="utf-8") as f:
    RESEARCH_PROMPT = f.read()

with open("prompts/doctor_prompt.txt", "r", encoding="utf-8") as f:
    DOCTOR_PROMPT = f.read()

with open("prompts/html_generator_prompt.txt", "r", encoding="utf-8") as f:
    HTML_GENERATOR_PROMPT = f.read()

PLAN_PROMPT = "Jsi výzkumný asistent, který pomáhá plánovat výzkum na základě zadaného úkolu."

class Agent:
    def __init__(self):
        # Inicializace modelu a klientů
        # Zde můžete přidat inicializaci OpenAI nebo jiného modelu
        self.model = None  # Zde nastavte váš model
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        
        # Vytvořte složku pro PDF soubory, pokud neexistuje
        os.makedirs("pdfs", exist_ok=True)

    async def query_node(self, state: AgentState) -> Dict[str, Any]:
        """Generuje dotazy na základě tématu"""
        # Implementace s OpenAI nebo jiným modelem
        # Pro testování použijeme simulovanou odpověď
        
        # Tady byste volali model.invoke(), například:
        # messages = [
        #     {"role": "system", "content": QUERY_PROMPT},
        #     {"role": "user", "content": f"Téma je: {state.topic}"}
        # ]
        # response = await self.model.invoke(messages)
        # content = response.content
        
        # Simulace response pro vývoj:
        content = f"**\"AI research in {state.topic}\"** **\"Machine Learning for {state.topic}\"**"
        queries = re.findall(r'\*\*"(.*?)"\*\*', content)
        return {"queries": queries}

    async def scholar_node(self, state: AgentState) -> Dict[str, Any]:
        """Vyhledává odborné články pomocí SerpAPI"""
        queries = state.queries
        results = []
        async with httpx.AsyncClient() as client:
            for q in queries:
                params = {
                    "api_key": os.getenv("SERP_API_KEY"),
                    "engine": "google_scholar",
                    "q": q,
                    "hl": "en"
                }
                r = await client.get("https://serpapi.com/search", params=params)
                data = r.json()
                for res in data.get("organic_results", []):
                    results.append((
                        res["title"],
                        res.get("publication_info", {}).get("authors", [{}])[0].get("name", ""),
                        res.get("resources", [{}])[0].get("link", ""),
                        res.get("snippet", "")
                    ))
        return {"articles": results}

    async def pdf_download_node(self, state: AgentState) -> Dict[str, Any]:
        """Stahuje PDF články z odkazů"""
        articles = state.articles
        downloaded_files = []
        
        for article in articles:
            title, author, link, snippet = article
            
            # Stáhneme PDF pokud je k dispozici
            try:
                response = httpx.get(link, timeout=10)
                if response.status_code == 200 and "pdf" in response.headers.get("content-type", ""):
                    filename = f"pdfs/{title[:50].replace('/', '_')}.pdf"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    downloaded_files.append(filename)
            except Exception as e:
                print(f"Chyba při stahování PDF: {e}")
                
        return {"downloaded_files": downloaded_files}

    async def plan_node(self, state: AgentState) -> Dict[str, Any]:
        """Vytvoří plán výzkumu na základě úkolu"""
        # Implementace s OpenAI nebo jiným modelem
        # messages = [
        #     {"role": "system", "content": PLAN_PROMPT},
        #     {"role": "user", "content": state.task}
        # ]
        # response = await self.model.invoke(messages)
        # plan = response.content
        
        # Simulace odpovědi pro vývoj:
        plan = f"Plán výzkumu pro téma {state.topic}:\n1. Shromáždit literaturu\n2. Analyzovat data\n3. Vytvořit shrnutí"
        return {"plan": plan}

    async def research_plan_node(self, state: AgentState) -> Dict[str, Any]:
        """Provádí výzkum pomocí Tavily API"""
        # Zde by měla být implementace s Tavily API
        # Pro vývoj použijeme simulovanou odpověď:
        content = state.content or []
        content.append(f"Výsledek výzkumu pro téma: {state.topic}\n")
        for article in state.articles[:3]:  # Omezíme na první 3 články
            title, author, link, snippet = article
            content.append(f"{title}\n{snippet}\n{link}\n")
            
        return {"content": content}

    async def doctor_node(self, state: AgentState) -> Dict[str, Any]:
        """Vytvoří diagnózu na základě příznaků a výzkumu"""
        # Implementace s OpenAI nebo jiným modelem
        # formatted_content = "\n".join(state.content)
        # messages = [
        #     {"role": "system", "content": DOCTOR_PROMPT.format(content=formatted_content)},
        #     {"role": "user", "content": state.task}
        # ]
        # response = await self.model.invoke(messages)
        # draft = response.content
        
        # Simulace odpovědi pro vývoj:
        draft = f"Diagnóza na základě příznaků:\n\nNA ZÁKLADĚ POSKYTNUTÝCH INFORMACÍ SE JEDNÁ O..."
        return {"draft": draft}

    async def html_generation_node(self, state: AgentState) -> Dict[str, Any]:
        """Generuje HTML verzi dokumentu"""
        # Implementace s OpenAI nebo jiným modelem
        # messages = [
        #     {"role": "system", "content": HTML_GENERATOR_PROMPT},
        #     {"role": "user", "content": state.draft}
        # ]
        # response = await self.model.invoke(messages)
        # html_content = response.content
        
        # Simulace odpovědi pro vývoj:
        html_content = f"""
        <!DOCTYPE html>
        <html lang="cs">
        <head>
            <meta charset="UTF-8">
            <title>{state.topic}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2c3e50; }}
                .source {{ color: #7f8c8d; font-size: 0.8em; }}
            </style>
        </head>
        <body>
            <h1>{state.topic}</h1>
            <div>{state.draft}</div>
            <hr>
            <h2>Zdroje</h2>
            <ul>
                {"".join(f'<li><a href="{article[2]}">{article[0]}</a> - {article[1]}</li>' for article in state.articles)}
            </ul>
        </body>
        </html>
        """
        return {"html_content": html_content}

    async def run_graph(self, initial_state: AgentState) -> AgentState:
        """Spouští celý workflow agenta"""
        state = initial_state.dict()
        
        # Krok 1: Generování dotazů
        update = await self.query_node(AgentState(**state))
        state.update(update)
        
        # Krok 2: Vyhledávání článků
        update = await self.scholar_node(AgentState(**state))
        state.update(update)
        
        # Krok 3: Vytvoření plánu výzkumu
        update = await self.plan_node(AgentState(**state))
        state.update(update)
        
        # Krok 4: Stažení PDF dokumentů (volitelné)
        pdf_update = await self.pdf_download_node(AgentState(**state))
        state.update(pdf_update)
        
        # Krok 5: Provedení výzkumu
        update = await self.research_plan_node(AgentState(**state))
        state.update(update)
        
        # Krok 6: Vytvoření diagnózy nebo shrnutí
        update = await self.doctor_node(AgentState(**state))
        state.update(update)
        
        # Krok 7: Generování HTML výstupu
        update = await self.html_generation_node(AgentState(**state))
        state.update(update)

        return AgentState(**state)
    
    
    
    
    import os
import re
import json
import requests 
import asyncio
from typing import Dict, Any, List, Tuple
from pathlib import Path

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.pydantic_v1 import BaseModel as LangchainBaseModel
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from tavily import TavilyClient
# from serpapi import GoogleSearch # Zakomentováno

from ..db.schemas import AgentState
from ..core.config import OPENAI_API_KEY, TAVILY_API_KEY # SERP_API_KEY odebráno

os.makedirs("checkpoints", exist_ok=True)
# pdfs složka se nebude používat, pokud pdf_download_node odstraníme
# os.makedirs("pdfs", exist_ok=True) 

memory = SqliteSaver.from_conn_string("checkpoints/agent.db")

PROMPTS_DIR_PATH = Path(__file__).parent.parent / "utils" / "prompts"

def load_prompt(file_name: str) -> str:
    prompt_file = PROMPTS_DIR_PATH / file_name
    try:
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Varování: Soubor s promptem {file_name} nebyl nalezen v {prompt_file}")
        return f"PROMPT '{file_name}' NOT FOUND"

QUERY_PROMPT = load_prompt("query_prompt.txt")
RESEARCH_PROMPT = load_prompt("research_prompt.txt") # Tento prompt by měl instruovat LLM k vytvoření dotazů pro Tavily
DOCTOR_PROMPT = load_prompt("doctor_prompt.txt")
HTML_GENERATOR_PROMPT = load_prompt("html_generator_prompt.txt")
PLAN_PROMPT_TEXT = load_prompt("plan_prompt.txt")
if PLAN_PROMPT_TEXT == "PROMPT 'plan_prompt.txt' NOT FOUND":
    PLAN_PROMPT_TEXT = "Jsi výzkumný asistent, který pomáhá plánovat výzkum na základě zadaného úkolu."


class Queries(LangchainBaseModel):
    queries: List[str]

class LangGraphAgent:
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY není nakonfigurován.")
        if not TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY není nakonfigurován.")

        self.model = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=OPENAI_API_KEY)
        self.tavily = TavilyClient(api_key=TAVILY_API_KEY)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        builder = StateGraph(AgentState)
        
        builder.add_node("query_builder", self.query_node)
        # builder.add_node("scholar", self.scholar_node) # Odebráno
        # builder.add_node("pdf_download", self.pdf_download_node) # Odebráno
        builder.add_node("plan", self.plan_node)
        builder.add_node("research", self.research_plan_node) # Tento uzel bude používat Tavily
        builder.add_node("doctor", self.doctor_node)
        builder.add_node("html_generator", self.html_generation_node)
        
        builder.set_entry_point("query_builder")
        
        # Upravené hrany grafu
        builder.add_edge("query_builder", "plan") # query_builder nyní vede přímo na plan
        # builder.add_edge("scholar", "pdf_download") # Odebráno
        # builder.add_edge("pdf_download", "plan") # Odebráno
        builder.add_edge("plan", "research")
        builder.add_edge("research", "doctor")
        builder.add_edge("doctor", "html_generator")
        builder.add_edge("html_generator", END)
        
        return builder.compile(checkpointer=memory)

    def query_node(self, state: Dict) -> Dict[str, Any]:
        agent_state = AgentState(**state)
        current_topic = agent_state.topic
        if not current_topic:
            return {"queries": []} # Vrátí prázdný seznam, pokud téma chybí

        messages = [
            SystemMessage(content=QUERY_PROMPT), # Tento prompt by měl generovat obecné dotazy nebo dotazy pro Tavily
            HumanMessage(content=f"Téma je: {current_topic}"),
        ]
        
        response = self.model.invoke(messages)
        content = response.content
        # Tento regex je pro formát **"dotaz"**. Ujistěte se, že váš QUERY_PROMPT generuje tento formát.
        queries = re.findall(r'\*\*\"(.*?)\"\*\*', content)
        # Tyto queries budou použity v research_plan_node pro Tavily
        return {"queries": queries, "articles": []} # Inicializujeme articles jako prázdný seznam

    # scholar_node a pdf_download_node jsou odstraněny

    def plan_node(self, state: Dict) -> Dict[str, Any]:
        agent_state = AgentState(**state)
        current_task = agent_state.task
        if not current_task:
            return {"plan": "Není zadán žádný úkol pro plánování."}
        messages = [
            SystemMessage(content=PLAN_PROMPT_TEXT), 
            HumanMessage(content=current_task)
        ]
        response = self.model.invoke(messages)
        return {"plan": response.content}

    def research_plan_node(self, state: Dict) -> Dict[str, Any]:
        agent_state = AgentState(**state)
        # Použijeme queries vygenerované v query_node, pokud existují,
        # nebo můžeme nechat Tavily pracovat přímo s task/topic.
        # Pro jednoduchost nyní použijeme queries z query_node.
        queries_for_tavily = agent_state.queries 
        current_task_or_topic = agent_state.task or agent_state.topic # Fallback na topic

        if not queries_for_tavily and not current_task_or_topic:
             return {"content": ["Nebyly poskytnuty žádné dotazy ani úkol/téma pro výzkum."]}

        content_list = agent_state.content or []
        
        # Pokud nemáme specifické dotazy, můžeme použít obecný dotaz založený na úkolu/tématu
        if not queries_for_tavily:
            queries_for_tavily = [current_task_or_topic]


        for q_text in queries_for_tavily:
            if not q_text: continue # Přeskočíme prázdné dotazy
            try:
                # Tavily může vyhledávat články, webové stránky atd.
                print(f"Tavily searching for: {q_text}")
                response = self.tavily.search(query=q_text, search_depth="advanced", max_results=5) # Zvýšen max_results
                
                for r_item in response.get('results', []):            
                    content_list.append(f"Zdroj: {r_item.get('url', 'N/A')}\nNázev: {r_item.get('title', '')}\nObsah: {r_item.get('content', '')}\n---")
            except Exception as e:
                print(f"Chyba během Tavily vyhledávání pro dotaz '{q_text}': {e}")
        return {"content": content_list}

    def doctor_node(self, state: Dict) -> Dict[str, Any]:
        agent_state = AgentState(**state)
        content_list = agent_state.content
        current_task = agent_state.task
        if not current_task or not content_list:
            return {"draft": "Nedostatek informací (úkolu nebo obsahu) pro vytvoření návrhu."}
            
        content_str = "\n\n".join(content_list)
        formatted_doctor_prompt = DOCTOR_PROMPT.format(content=content_str) # Ujistěte se, že DOCTOR_PROMPT má {content}
        messages = [
            SystemMessage(content=formatted_doctor_prompt),
            HumanMessage(content=current_task)
        ]
        response = self.model.invoke(messages)
        return {"draft": response.content}

    def html_generation_node(self, state: Dict) -> Dict[str, Any]:
        agent_state = AgentState(**state)
        draft_content = agent_state.draft
        # articles = agent_state.articles # articles nebudou naplněny, pokud nepoužíváme scholar_node
                                        # Můžete sem přidat odkazy z Tavily, pokud je chcete zobrazit.

        if not draft_content:
            return {"html_content": "<html><body><p>Nebyl vytvořen žádný návrh (draft) pro generování HTML.</p></body></html>"}
            
        # Jednoduché HTML generování, můžete ho vylepšit
        html_body = f"<h1>{agent_state.topic or 'Výstup agenta'}</h1>\n"
        html_body += f"<h2>Úkol:</h2>\n<p>{agent_state.task}</p>\n"
        html_body += f"<h2>Plán:</h2>\n<p>{agent_state.plan.replace('\n', '<br>')}</p>\n"
        html_body += f"<h2>Výzkum (shrnutí obsahu):</h2>\n<div>{draft_content.replace('\n', '<br>')}</div>\n"
        
        # Pokud chcete zobrazit zdroje z Tavily (z pole content)
        # html_body += "<h2>Zdroje z výzkumu:</h2><ul>"
        # for item in agent_state.content:
        #     # Předpokládáme formát "Zdroj: URL\nNázev: TITLE\nObsah: CONTENT"
        #     parts = item.split('\n')
        #     url_part = parts[0] if len(parts) > 0 else ""
        #     title_part = parts[1] if len(parts) > 1 else ""
        #     url = url_part.replace("Zdroj: ", "")
        #     title = title_part.replace("Název: ", "")
        #     if url and title:
        #         html_body += f'<li><a href="{url}" target="_blank">{title}</a></li>'
        # html_body += "</ul>"


        final_html = f"<!DOCTYPE html><html lang='cs'><head><meta charset='UTF-8'><title>Výstup Agenta</title></head><body>{html_body}</body></html>"
        
        # Pokud by LLM generoval HTML:
        # messages = [
        #     SystemMessage(content=HTML_GENERATOR_PROMPT), # Tento prompt by měl instruovat LLM k vytvoření HTML
        #     HumanMessage(content=draft_content) # Nebo můžete poslat celý agent_state.dict() jako kontext
        # ]
        # response = self.model.invoke(messages)
        # html_output = response.content
        # if html_output.strip().startswith("```html"):
        #     html_output = re.sub(r"^\s*```html\s*", "", html_output, flags=re.MULTILINE)
        #     html_output = re.sub(r"\s*```\s*$", "", html_output, flags=re.MULTILINE)
        # final_html = html_output.strip()
            
        return {"html_content": final_html}

    async def run_graph_async(self, initial_state_dict: Dict, thread_id: str) -> Dict:
        config = {"configurable": {"thread_id": thread_id}}
        final_state_values = await self.graph.ainvoke(initial_state_dict, config=config)
        return final_state_values

    async def stream_graph_updates_async(self, initial_state_dict: Dict, thread_id: str):
        config = {"configurable": {"thread_id": thread_id}}
        async for update_chunk in self.graph.astream(initial_state_dict, config=config, stream_mode="updates"):
            yield update_chunk