import os
import importlib

TOOLS_DEFINITIONS = [] #list of definitions for FE
TOOL_IMPLEMENTATIONS = {} #dict 

TOOL_DIR = os.path.dirname(__file__)

for filename in os.listdir(TOOL_DIR):
    if filename.endswith(".py") and not filename.startswith("__"):
        module_name = f"app.utils.tools.{filename[:-3]}"
        
        try:
            module = importlib.import_module(module_name)
            
            if hasattr(module, "TOOL_DEFINITION"):
                definition = module.TOOL_DEFINITION
                TOOLS_DEFINITIONS.append(definition)
                
                if hasattr(module, "get_tool"):
                    tool_name = definition.get("name")
                    if tool_name:
                        TOOL_IMPLEMENTATIONS[tool_name] = module.get_tool

        except ImportError as e:
            print(f"Chyba při importu nástroje {module_name}: {e}")
            
            
            
            
            
                
"""
from langchain.tools import Tool
from typing import Optional

TOOL_DEFINITION = {
    "name": 
    "description":
    "parameters": [
        {
            "name": "query",
            "type": "string",
            "description": "Vyhledávací dotaz, který se má položit vyhledávači."
        }
    ]
}

def get_tool() -> Tool:

return

"""