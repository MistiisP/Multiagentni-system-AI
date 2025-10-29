from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import Tool
from typing import Optional

TOOL_DEFINITION = {
    "name": "tavily_search",
    "description": "Vyhledá informace na internetu pomocí Tavily.",
    "required_provider": "tavily",
    "parameters": [
        {
            "name": "query",
            "type": "string",
            "description": "Vyhledávací dotaz, který se má položit vyhledávači."
        }
    ]
}

def get_tool(api_key: Optional[str] = None) -> Tool:
    if not api_key:
        raise ValueError("Tavily Search tool need an API key")

    tavily_tool_instance = TavilySearchResults(
        max_results=1,
        tavily_api_key=api_key
    )

    return Tool(
        name=TOOL_DEFINITION["name"],
        func=tavily_tool_instance.run,
        description=TOOL_DEFINITION["description"]
    )