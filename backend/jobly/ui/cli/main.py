"""CLI main entry point."""

import click
from .commands import (
    profile_cmd,
    search_cmd,
    apply_cmd,
    track_cmd,
    network_cmd,
    analytics_cmd
)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Jobly - AI-powered job search automation."""
    # Command group entrypoint.
    return None


# Register command groups
cli.add_command(profile_cmd, name="profile")
cli.add_command(search_cmd, name="search")
cli.add_command(apply_cmd, name="apply")
cli.add_command(track_cmd, name="track")
cli.add_command(network_cmd, name="network")
cli.add_command(analytics_cmd, name="analytics")


if __name__ == "__main__":
    cli()
