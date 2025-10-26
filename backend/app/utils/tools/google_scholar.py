from langchain_community.tools.google_scholar import GoogleScholarQueryRun
from langchain_community.utilities.google_scholar import GoogleScholarAPIWrapper
from langchain.tools import Tool

TOOL_DEFINITION = {
    "name": "google_scholar_search",
    "description": "Vyhledá odborné články pomocí Google Scholar.",
    "parameters": [
        {
            "name": "query",
            "type": "string",
            "description": "Vyhledávací dotaz pro Google Scholar."
        }
    ]
}

def get_tool() -> Tool:
    api_wrapper = GoogleScholarAPIWrapper()
    scholar_tool = GoogleScholarQueryRun(api_wrapper=api_wrapper)
    
    return Tool(
        name=TOOL_DEFINITION["name"],
        func=scholar_tool.run,
        description=TOOL_DEFINITION["description"]
    )
