import typer
from pathlib import Path
from .knowledge_manager import validate_file, SCHEMA_MAP

app = typer.Typer()

@app.command()
def validate(
    file_path: Path = typer.Argument(..., help="Path to the JSONL file to validate"),
    type: str = typer.Option(..., help="Type of knowledge (glossary, dataset, rule, analysis)")
):
    """
    Validate a JSONL file against the defined schema.
    """
    if type not in SCHEMA_MAP:
        typer.echo(f"Invalid type. Must be one of: {', '.join(SCHEMA_MAP.keys())}")
        raise typer.Exit(code=1)

    if validate_file(file_path, type):
        typer.echo(f"Validation successful: {file_path}")
    else:
        typer.echo(f"Validation failed: {file_path}")
        raise typer.Exit(code=1)

@app.command()
def build_index():
    """
    Build the RAG index from approved knowledge.
    """
    from .rag_engine import build_index
    # For now, we index raw data for testing if approved is empty, or just approved.
    # Plan says approved, but for verification we might want to test with raw if approved is empty.
    # Let's stick to the plan: source from approved.
    # BUT for the immediate test, I'll allow indexing raw if specified or just copy sample to approved.
    # Let's just point to approved, and I will move the sample file to approved in the verification step.

    approved_dir = Path("ai_knowledge/approved")
    if not approved_dir.exists():
        approved_dir.mkdir(parents=True)

    typer.echo(f"Building index from {approved_dir}...")
    try:
        build_index(approved_dir)
        typer.echo("Index built successfully.")
    except Exception as e:
        typer.echo(f"Error building index: {e}")
        raise typer.Exit(code=1)

@app.command()
def reset_index():
    """
    Delete the existing index (collection) in Qdrant.
    Use this when changing embedding models.
    """
    from .rag_engine import reset_index
    try:
        reset_index()
        typer.echo("Index reset successfully.")
    except Exception as e:
        typer.echo(f"Error resetting index: {e}")
        raise typer.Exit(code=1)

@app.command()
def search(query: str = typer.Argument(..., help="Query string")):
    """
    Search the knowledge base.
    """
    from .rag_engine import search
    try:
        result = search(query)
        typer.echo(f"Result: {result}")
    except Exception as e:
        typer.echo(f"Error searching: {e}")
        raise typer.Exit(code=1)

@app.command()
def add(
    data: str = typer.Argument(..., help="JSON string of the knowledge item"),
    type: str = typer.Option(..., help="Type of knowledge (glossary, dataset, rule, analysis)")
):
    """
    Add a new knowledge item to the raw knowledge base.
    """
    import json
    from .schemas import GlossaryItem, DatasetItem, RuleItem, AnalysisItem

    if type not in SCHEMA_MAP:
        typer.echo(f"Invalid type. Must be one of: {', '.join(SCHEMA_MAP.keys())}")
        raise typer.Exit(code=1)

    try:
        item_data = json.loads(data)
        # Validate and create item using Pydantic model to ensure ID and timestamps are generated
        schema = SCHEMA_MAP[type]
        item = schema(**item_data)

        # Ensure author is set to 'ai_agent' if not provided, or keep default 'user' but maybe we want to distinguish?
        # The schema default is 'user'. The AI calling this might want to override it, but for now let's stick to the input.
        # Actually, if the AI calls it, it might be good to set author="ai_agent" if not present.
        if "author" not in item_data:
             item.author = "ai_agent"

        # Append to file
        file_path = Path(f"ai_knowledge/raw/{type}.jsonl")
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True)

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(item.model_dump_json() + "\n")

        typer.echo(f"Added item to {file_path}")

    except json.JSONDecodeError:
        typer.echo("Invalid JSON string.")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error adding item: {e}")
        raise typer.Exit(code=1)

@app.command()
def serve_mcp():
    """
    Start the MCP server.
    """
    from .mcp_server import mcp
    # FastMCP.run() handles stdio communication by default when run as script
    # But here we are calling it from typer.
    # mcp.run() uses uvicorn if transport is sse, or stdio if stdio.
    # Default FastMCP is stdio.
    mcp.run()

if __name__ == "__main__":
    app()
