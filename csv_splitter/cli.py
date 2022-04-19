from pathlib import Path
from typing import Optional

import typer

from .dump_splitter import DumpSplitter
from .settings import ORIGINAL_FILE_PATH_ENV_NAME
from .utils import get_cli_version


app = typer.Typer()


@app.command()
def split(
        original_file_path: Path = typer.Argument(
            ...,
            help='The path of a csv file that needs to be split into several csv files.',
            envvar=ORIGINAL_FILE_PATH_ENV_NAME,
            exists=True,
            readable=True,
        ),
        lines_limit_for_one_file: int = typer.Option(
            250_000,
            '--lines_limit_for_one_file',
            '-l',
            help='The limit of lines in new csv files',
        ),
        column_number_to_filter: int = typer.Option(
            1,
            '--column_number_to_filter',
            '-c',
            help='The column number which is used to filter rows. '
                 'Have in mind that the counting starts from zero not from one.',
            min=0,
            max=2,
        ),
        output_dir_path: Path = typer.Option(
            './',
            '--output_dir_path',
            '-o',
            help='The path of a dir where new csv files will be reside. Keep in mind it is your '
                 'responsibility to check correctness of this path.',
            exists=True,
            writable=True,
        ),
        only_ids: bool = typer.Option(
            False,
            '--only-ids',
            '-i',
            help='There will be only one column (mobile) in generated csv files',
        ),
        header: bool = typer.Option(
            False,
            '--enable-header',
            '-h',
            help='Whether include or not a header of the column',
        ),
) -> None:
    """
    The command for splitting csv file into several csv files with preserving a
    structure of the csv file. The original file must have the following structure:
    city_full-region_nm-mobile.
    """
    dump_splitter = DumpSplitter(
        original_file_path=original_file_path.absolute().__str__(),
        lines_limit_for_one_file=lines_limit_for_one_file,
        column_number_to_filter=column_number_to_filter,
        output_dir_path=output_dir_path.absolute().__str__(),
        only_ids=only_ids,
        header=header,
    )
    dump_splitter.split_csv_file()


@app.callback()
def callback(
        version: Optional[bool] = typer.Option(
            None,
            '--version',
            callback=get_cli_version,
            is_eager=True,
            help='Show the current version of this the cli app',
        ),
) -> None:
    """
    CVS dumps splitter
    """


if __name__ == '__main__':
    app()
