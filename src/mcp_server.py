from mcp.server.fastmcp import FastMCP
from .rag_engine import search

# Initialize FastMCP server
mcp = FastMCP("OJT Agent Knowledge Server")

@mcp.tool()
def search_knowledge(query: str) -> str:
    """
    Search the OJT Agent's knowledge base for relevant information.
    Use this tool when you need to recall definitions, datasets, rules, or past analyses.

    Args:
        query: The search query string.
    """
    try:
        return search(query)
    except Exception as e:
        return f"Error searching knowledge: {str(e)}"

if __name__ == "__main__":
    mcp.run()
