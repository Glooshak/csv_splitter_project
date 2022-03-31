import typer

from . import __version__


def get_cli_version(value: bool) -> None:
    if value:
        typer.echo(f'Splitter for csv dumps version: {__version__}')
        raise typer.Exit
