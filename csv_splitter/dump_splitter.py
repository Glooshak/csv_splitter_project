import csv
from uuid import uuid4
import logging

from transliterate import translit


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DumpSplitter:

    def __init__(
            self,
            original_file_path: str,
            lines_limit_for_one_file: int = 250_000,
            column_number_to_filter: int = 1,
            output_dir_path: str = './',
            only_ids: bool = False,
            header: bool = False,
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
        self._only_ids = only_ids
        self._header = header

    def _write_new_file(
            self,
            current_region: str,
            content: list[str],
    ) -> None:
        file_id = uuid4()
        current_region: str = translit(current_region, 'ru', reversed=True).replace('.', '').replace(' ', '_')
        with open(f'{self._output_dir_path}/{current_region}_{file_id}.csv', 'w', newline='') as new_csv_file:
            writer = csv.writer(new_csv_file)
            writer.writerows(content)
            logger.info(f'The new file was written for a region: [{current_region}] with id: {file_id}')

    def split_csv_file(self) -> None:
        logger.info(f'Started splitting a file {self._original_file_path}')
        with open(self._original_file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                if reader.line_num == 1:
                    self._fields_names = line if not self._only_ids else list([line[2]])
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

                if self._counter == 0 and self._header:
                    self._buffer.append(self._fields_names)

                if not self._only_ids:
                    self._buffer.append(line)
                else:
                    self._buffer.append([line[2]])
                self._counter += 1
                self._previous_region = self._current_region

        # Don't forget to write the last chunk of a splitting process
        logger.info(f'Flushing a buffer by writing the last file')
        self._write_new_file(self._current_region, self._buffer)
        logger.info(f'Successfully split the file {self._original_file_path}')
