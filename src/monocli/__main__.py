"""Entry point for Mono CLI.

Run the dashboard with: python -m monocli
"""

import argparse

from monocli import __version__, configure_logging, get_logger
from monocli.ui.app import MonoApp


def main() -> None:
    """Run the Mono CLI dashboard application."""
    parser = argparse.ArgumentParser(
        description="Mono CLI Dashboard - Unified view of PRs and work items"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    args = parser.parse_args()

    configure_logging(debug=args.debug)
    logger = get_logger()
    logger.info("Starting Mono CLI", version=__version__, debug_mode=args.debug)

    app = MonoApp()
    app.run()


if __name__ == "__main__":
    main()
