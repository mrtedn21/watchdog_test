import csv
import re
from pathlib import Path

from dateutil.parser import parse
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def from_any_date_to_iso(any_date: str):
    date_obj = parse(any_date)
    return date_obj.strftime('%Y-%m-%d')


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        with open(event.src_path, 'r') as f:
            file_name = Path(event.src_path).stem
            parsed_file_name = re.fullmatch(
                '(\d{8})_(\d{1,})_(.{1,})',
                file_name
            ).groups()

            result_obj = {
                'flt': int(parsed_file_name[1]),
                'date': from_any_date_to_iso(parsed_file_name[0]),
                'dep': parsed_file_name[2],
                'prl': [],
            }

            csv_obj = csv.reader(f, delimiter=';')
            for row in csv_obj:
                if not row:
                    continue

                result_obj['prl'].append({
                    'num': row[0],
                    'surname': row[1],
                    'firstname': row[2],
                    'bdate': from_any_date_to_iso(row[3]),
                })

            print(result_obj)


if __name__ == '__main__':
    working_directory = str(Path.cwd() / 'working_directory' / 'In')
    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, working_directory, recursive=True)
    observer.start()

    try:
        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()
