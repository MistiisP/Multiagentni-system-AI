from langchain_community.tools.google_scholar import GoogleScholarQueryRun
from langchain_community.utilities.google_scholar import GoogleScholarAPIWrapper
from langchain.tools import Tool

TOOL_DEFINITION = {
    "name": "google_scholar_search",
    "description": "Vyhledá odborné články pomocí Google Scholar.",
    "required_provider": None,
    "parameters": [
        {
            "name": "query",
            "type": "string",
            "description": "Vyhledávací dotaz pro pro vyhledávání vědeckých publikací přes Google Scholar."
        }
    ]
}

def search_google_scholar(query: str) -> str:
    """
    Vyhledá články přes Google Scholar.
    """
    try:
        api_wrapper = GoogleScholarAPIWrapper()
        scholar_tool = GoogleScholarQueryRun(api_wrapper=api_wrapper)
        result = scholar_tool.run(query)
        if result and "No good Google Scholar Result was found" not in result:
            return f"[Google Scholar Results]\n{result}"
        return "No good Google Scholar Result was found. Try refining your search query."
    except Exception as e:
        return f"Error searching Google Scholar: {str(e)}"
        
def get_tool() -> Tool:
    return Tool(
        name=TOOL_DEFINITION["name"],
        func=search_google_scholar,
        description=TOOL_DEFINITION["description"]
    )
