"""Network connectivity testing tools."""

from __future__ import annotations

import asyncio
import json
import statistics
import typing as t

import httpx
import typer

from monokl import get_logger
from monokl.db.network_store import NetworkStore
from monokl.db.network_store import PingResult

logger = get_logger(__name__)

# Constants
MS_PER_SECOND = 1000

network_app = typer.Typer(
    name="network",
    help="Network connectivity testing tools",
    no_args_is_help=True,
)

# Unicode block characters for sparkline (8 levels)
SPARKLINE_CHARS = "▁▂▃▄▅▆▇█"


def _make_sparkline(values: list[float]) -> str:
    """Create a Unicode sparkline from numeric values.

    Args:
        values: List of numeric values.

    Returns:
        Sparkline string using Unicode block characters.
    """
    if not values:
        return ""

    min_val = min(values)
    max_val = max(values)
    range_val = max_val - min_val

    if range_val == 0:
        return SPARKLINE_CHARS[3] * len(values)  # middle char if all same

    result = []
    for v in values:
        # Normalize to 0-7 range
        normalized = (v - min_val) / range_val
        index = min(7, int(normalized * 8))
        result.append(SPARKLINE_CHARS[index])

    return "".join(result)


def _format_response_time(ms: int | None) -> str:
    """Format response time for display."""
    if ms is None:
        return "N/A"
    if ms < MS_PER_SECOND:
        return f"{ms}ms"
    return f"{ms / MS_PER_SECOND:.2f}s"


async def _ping_url(url: str) -> tuple[bool, int | None, int | None, str | None]:
    """Ping a URL and measure response time.

    Args:
        url: URL to ping.

    Returns:
        Tuple of (success, response_time_ms, status_code, error_message).
    """
    try:
        async with httpx.AsyncClient() as client:
            start = asyncio.get_event_loop().time()
            response = await client.head(url, follow_redirects=True)
            elapsed = asyncio.get_event_loop().time() - start
            response_time_ms = int(elapsed * MS_PER_SECOND)
            return True, response_time_ms, response.status_code, None
    except httpx.TimeoutException:
        return False, None, None, "Timeout"
    except httpx.HTTPStatusError as e:
        elapsed = asyncio.get_event_loop().time() - start
        return False, int(elapsed * MS_PER_SECOND), e.response.status_code, str(e)
    except (httpx.ConnectError, httpx.ReadError, httpx.WriteError, OSError) as e:
        return False, None, None, str(e)


@network_app.command()
def ping(
    url: t.Annotated[str, typer.Argument(help="URL to ping")],
    timeout: t.Annotated[
        float, typer.Option("--timeout", "-t", help="Timeout in seconds")
    ] = 10.0,
    store: t.Annotated[  # noqa: FBT002
        bool, typer.Option("--store", "-s", help="Store result in database")
    ] = False,
    json_output: t.Annotated[  # noqa: FBT002
        bool, typer.Option("--json", "-j", help="Output as JSON")
    ] = False,
) -> None:
    """Ping a URL and measure response time."""

    async def _run_ping() -> tuple[bool, int | None, int | None, str | None]:
        async with asyncio.timeout(timeout):
            return await _ping_url(url)

    async def _run_and_store() -> tuple[bool, int | None, int | None, str | None]:
        try:
            result = await _run_ping()
        except TimeoutError:
            return False, None, None, f"Timeout after {timeout}s"

        if store:
            store_obj = NetworkStore()
            try:
                await store_obj.save_ping(
                    url=url,
                    response_time_ms=result[1],
                    status_code=result[2],
                    success=result[0],
                    error=result[3],
                )
            finally:
                await store_obj.close()
        return result

    success, response_time_ms, status_code, error = asyncio.run(_run_and_store())

    if json_output:
        result = {
            "url": url,
            "success": success,
            "response_time_ms": response_time_ms,
            "status_code": status_code,
            "error": error,
        }
        typer.echo(json.dumps(result))
    elif success:
        status_icon = "✓"
        status_text = f"OK ({status_code})"
        time_text = _format_response_time(response_time_ms)
        typer.echo(f"{status_icon} {url} - {status_text} - {time_text}")
    else:
        typer.echo(f"✗ {url} - FAIL - {error}", err=True)
        raise typer.Exit(1)


@network_app.command("report")
def report(
    url: t.Annotated[
        str | None,
        typer.Option("--url", "-u", help="Filter by URL"),
    ] = None,
    last: t.Annotated[
        int, typer.Option("--last", "-n", help="Number of results to show")
    ] = 20,
) -> None:
    """Show ping history with ASCII chart."""

    async def _get_report() -> list[PingResult]:
        store = NetworkStore()
        try:
            return await store.get_pings(url=url, limit=last)
        finally:
            await store.close()

    pings = asyncio.run(_get_report())

    if not pings:
        typer.echo("No ping results found.")
        raise typer.Exit

    # Reverse to show oldest first in chart
    pings_display = list(reversed(pings))

    if url:
        typer.echo(f"URL: {url} (last {len(pings)} checks)")
    else:
        typer.echo(f"Ping report (last {len(pings)} checks)")
        # Group by URL if no filter
        urls = {p.url for p in pings}
        if len(urls) > 1:
            typer.echo(f"URLs: {', '.join(sorted(urls))}")

    typer.echo("━" * 50)

    # Get successful response times for sparkline
    times = [p.response_time_ms for p in pings_display if p.response_time_ms is not None]
    if times:
        sparkline = _make_sparkline([float(t) for t in times])
        typer.echo(f"{sparkline}  (response time trend)")
    else:
        typer.echo("(no response time data)")

    typer.echo("━" * 50)

    # Stats
    success_count = sum(1 for p in pings if p.success)
    fail_count = len(pings) - success_count

    if times:
        avg_time = int(statistics.mean(times))
        min_time = min(times)
        max_time = max(times)
        typer.echo(
            f"✓ {success_count}/{len(pings)} successful  "
            f"|  avg: {_format_response_time(avg_time)}  "
            f"|  min: {_format_response_time(min_time)}  "
            f"|  max: {_format_response_time(max_time)}"
        )
    else:
        typer.echo(f"✓ {success_count}/{len(pings)} successful")

    if fail_count > 0:
        typer.echo(f"✗ {fail_count} failed")


@network_app.command("clear")
def clear(
    url: t.Annotated[
        str | None,
        typer.Option("--url", "-u", help="Clear only this URL"),
    ] = None,
    force: t.Annotated[  # noqa: FBT002
        bool, typer.Option("--force", "-f", help="Skip confirmation")
    ] = False,
) -> None:
    """Clear ping history."""
    if not force:
        target = url or "all URLs"
        confirm = typer.confirm(f"Clear ping history for {target}?")
        if not confirm:
            raise typer.Abort

    async def _clear() -> int:
        store = NetworkStore()
        try:
            return await store.clear_pings(url=url)
        finally:
            await store.close()

    deleted = asyncio.run(_clear())
    typer.echo(f"Cleared {deleted} ping record(s).")
