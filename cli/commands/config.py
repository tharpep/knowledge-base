"""Config command - display current configuration"""
import typer

from ..utils import check_venv


def config() -> None:
    """Show current configuration settings"""
    if not check_venv():
        raise typer.Exit(1)

    typer.echo("=== Current Configuration ===")
    typer.echo("")

    try:
        from core.config import get_config

        config = get_config()

        typer.echo("=== Primary Configuration ===")
        typer.echo("")
        
        typer.echo("Provider Configuration:")
        typer.echo(f"  Type: {config.provider_type}")
        typer.echo(f"  Name: {config.provider_name}")
        if config.provider_fallback:
            typer.echo(f"  Fallback: {config.provider_fallback}")
        typer.echo("")

        typer.echo("Model Configuration:")
        typer.echo(f"  Active Model: {config.model_name}")
        typer.echo(f"  Embedding Model: {config.embedding_model}")
        typer.echo("")

        typer.echo("Ollama Configuration:")
        typer.echo(f"  Base URL: {config.ollama_base_url}")
        typer.echo(f"  Timeout: {config.ollama_timeout}s")
        typer.echo("")

        typer.echo("Library Configuration:")
        typer.echo(f"  Storage: {'Persistent' if config.storage_use_persistent else 'In-memory'}")
        typer.echo(f"  Collection: {config.library_collection_name}")
        typer.echo(f"  Chunk Size: {config.library_chunk_size}")
        typer.echo(f"  Chunk Overlap: {config.library_chunk_overlap}")
        typer.echo("")

        typer.echo("Chat Context Configuration:")
        typer.echo(f"  Context Enabled: {config.chat_context_enabled}")
        typer.echo(f"  Library Enabled: {config.chat_library_enabled}")
        typer.echo(f"  Library Top-K: {config.chat_library_top_k}")
        typer.echo(f"  Journal Enabled: {config.chat_journal_enabled}")
        typer.echo(f"  Journal Top-K: {config.chat_journal_top_k}")
        typer.echo("")

        typer.echo("API Keys:")
        typer.echo(f"  Purdue: {'Set' if config.purdue_api_key else 'Not set'}")
        typer.echo(f"  OpenAI: {'Set' if config.openai_api_key else 'Not set'}")
        typer.echo(f"  Anthropic: {'Set' if config.anthropic_api_key else 'Not set'}")
        typer.echo("")

        typer.echo("Note: Override settings via .env file or environment variables")

    except ImportError as e:
        typer.echo(f"Error: Could not import config module: {e}", err=True)
        raise typer.Exit(1)

    raise typer.Exit(0)

