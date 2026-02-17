"""Entry point for Mono CLI.

Run the dashboard with: python -m monocli
Run setup with: python -m monocli setup
"""

import os
import sys
import typing as t
import webbrowser

import typer

from monocli import __version__
from monocli import configure_logging
from monocli import get_logger
from monocli.config import ConfigError
from monocli.config import validate_keyring_available
from monocli.db.connection import DatabaseManager
from monocli.db.work_store import WorkStore
from monocli.ui.app import MonoApp

app = typer.Typer(
    help="Mono CLI Dashboard - Unified view of PRs and work items",
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"monocli {__version__}")
        raise typer.Exit()


def _apply_env_vars(offline: bool, db_path: str | None) -> None:
    if offline:
        os.environ["MONOCLI_OFFLINE_MODE"] = "true"
    if db_path:
        os.environ["MONOCLI_DB_PATH"] = db_path


async def _clear_cache(db_path: str | None = None) -> None:
    db = DatabaseManager(db_path)
    async with db:
        from monocli.sources.registry import SourceRegistry

        store = WorkStore(SourceRegistry())
        await store.invalidate()


@app.callback()
def main_callback(
    version: bool = typer.Option(
        False, "--version", "-v", help="Show version and exit", callback=version_callback
    ),
) -> None:
    pass


@app.command()
def tui(
    debug: t.Annotated[bool, typer.Option("--debug", help="Enable debug logging")] = False,
    offline: t.Annotated[bool, typer.Option("--offline", help="Use cached data only")] = False,
    db_path: t.Annotated[
        str | None,
        typer.Option("--db-path", help="Path to SQLite database file"),
    ] = None,
    clear_cache: t.Annotated[
        bool,
        typer.Option("--clear-cache", help="Clear all cached data and exit"),
    ] = False,
) -> None:
    import asyncio

    configure_logging(debug=debug)
    logger = get_logger()
    logger.info("Starting Mono CLI TUI", version=__version__, debug_mode=debug)

    if clear_cache:
        try:
            asyncio.run(_clear_cache(db_path))
            typer.echo("Cache cleared successfully.")
            raise typer.Exit()
        except Exception as e:
            typer.echo(f"Error clearing cache: {e}", err=True)
            raise typer.Exit(1)

    _apply_env_vars(offline, db_path)

    try:
        validate_keyring_available()
    except ConfigError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    mono_app = MonoApp()
    mono_app.run()


@app.command()
def setup(
    debug: t.Annotated[bool, typer.Option("--debug", help="Enable debug logging")] = False,
) -> None:
    configure_logging(debug=debug)
    logger = get_logger()
    logger.info("Starting Mono CLI Setup", version=__version__, debug_mode=debug)

    try:
        validate_keyring_available()
    except ConfigError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    mono_app = MonoApp(initial_screen="setup")
    mono_app.run()


@app.command()
def web(
    port: t.Annotated[int, typer.Option("--port", "-p", help="Port for web server")] = 6969,
    no_open: t.Annotated[
        bool,
        typer.Option("--no-open", help="Don't open browser automatically"),
    ] = False,
    debug: t.Annotated[bool, typer.Option("--debug", help="Enable debug logging")] = False,
    offline: t.Annotated[bool, typer.Option("--offline", help="Use cached data only")] = False,
    db_path: t.Annotated[
        str | None,
        typer.Option("--db-path", help="Path to SQLite database file"),
    ] = None,
) -> None:
    from textual_serve.server import Server

    configure_logging(debug=debug)
    logger = get_logger()
    logger.info("Starting Mono CLI Web Server", version=__version__, port=port)

    _apply_env_vars(offline, db_path)

    try:
        validate_keyring_available()
    except ConfigError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None

    cmd_parts = [sys.executable, "-m", "monocli", "tui"]
    if debug:
        cmd_parts.append("--debug")
    if offline:
        cmd_parts.append("--offline")
    if db_path:
        cmd_parts.extend(["--db-path", db_path])

    host = "localhost"
    server = Server(" ".join(cmd_parts), host=host, port=port)

    url = f"http://{host}:{port}"
    typer.echo(f"Starting web server at {url}")

    if not no_open:
        typer.echo("Opening browser...")
        webbrowser.open(url)

    server.serve()


if __name__ == "__main__":
    app()
