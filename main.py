from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        print(event.src_path)


if __name__ == '__main__':
    working_directory = str(Path.cwd() / 'working_directory')
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
