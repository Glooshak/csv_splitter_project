import csv
from pathlib import Path
from uuid import uuid4
import logging
from typing import Optional

import typer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DumpSplitter:

    def __init__(
            self,
            original_file_path: str,
            lines_limit_for_one_file: int = 250_000,
            column_number_to_filter: int = 1,
            output_dir_path: str = './'
    ) -> None:
        self._original_file_path = original_file_path
        self._cities_limit_for_one_file = lines_limit_for_one_file
        self._column_number_to_filter = column_number_to_filter
        self._output_dir_path = output_dir_path
        self._current_region = None
        self._previous_region = None
        self._buffer = list()
        self._fields_names = list()
        self._counter = 0

    def _write_new_file(
            self,
            current_region: str,
            content: list[str],
    ) -> None:
        file_id = uuid4()
        with open(f'{self._output_dir_path}/{current_region}_{file_id}.csv', 'w', newline='', encoding='cp1251') as new_csv_file:
            writer = csv.writer(new_csv_file)
            writer.writerows(content)
            logger.info(f'The new file was written for a region: [{current_region}] with id: {file_id}')

    def split_csv_file(self) -> None:
        logger.info(f'Started splitting a file {self._original_file_path}')
        with open(self._original_file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                if reader.line_num == 1:
                    self._fields_names = line
                    continue

                self._current_region = line[self._column_number_to_filter]
                self._previous_region = self._current_region if self._previous_region is None else self._previous_region
                is_reached_limit = self._counter == self._cities_limit_for_one_file
                is_new_region = self._current_region != self._previous_region

                if is_reached_limit or is_new_region:
                    logger.info(f'Began to write a new file because '
                                f'{"reached a rows number limit" if is_reached_limit else "found a new region name"}')
                    self._write_new_file(self._previous_region, self._buffer)
                    self._buffer.clear()
                    self._counter = 0

                if self._counter == 0:
                    self._buffer.append(self._fields_names)

                self._buffer.append(line)
                self._counter += 1
                self._previous_region = self._current_region

        # Don't forget to write the last chunk of a splitting process
        logger.info(f'Flushing a buffer by writing the last file')
        self._write_new_file(self._current_region, self._buffer)
        logger.info(f'Successfully split the file {self._original_file_path}')


__version__ = '0.1.0'
ORIGINAL_FILE_PATH_ENV_NAME = 'CSV_SPLITTER_FILE_PATH'


def get_cli_version(value: bool) -> None:
    if value:
        typer.echo(f'Splitter for csv dumps version: {__version__}')
        raise typer.Exit


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
        version: Optional[bool] = typer.Option(
            None,
            '--version',
            callback=get_cli_version,
            is_eager=True,
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
    )
    dump_splitter.split_csv_file()


@app.callback()
def callback() -> None:
    """
    CVS dumps splitter
    """


if __name__ == '__main__':
    app()

