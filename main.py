import csv
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        with open(event.src_path, 'r') as f:
            csv_obj = csv.reader(f, delimiter=';')
            for row in csv_obj:
                print(', '.join(row))


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
