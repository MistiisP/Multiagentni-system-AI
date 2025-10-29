from bs4 import BeautifulSoup
from ddgs import DDGS
from langchain.tools import Tool

TOOL_DEFINITION = {
    "name": "duckduckgo_search",
    "description": "Vyhledá webové stránky pomocí DuckDuckGo.",
    "required_provider": None,
    "parameters": [
        {
            "name": "query",
            "type": "string",
            "description": "Vyhledávací dotaz pro DuckDuckGo."
        },
        {
            "name": "max_result",
            "type": "integer",
            "description": "Maximální počet výsledků."
        }
    ]
}

def duckduckgo_search_web(query: str, max_result: int = 5) -> Tool:
    duckduckgo = DDGS()
    try:
        results = duckduckgo.text(query, max_results=max_result)
        return "\n".join([f"{i['title']}: {i['href']}" for i in results])
    except Exception as e:
        return f"Search failed: {str(e)}"

def get_tool() -> Tool:
    return Tool(
        name=TOOL_DEFINITION["name"],
        func=duckduckgo_search_web,
        description=TOOL_DEFINITION["description"]
    )