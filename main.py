from pathlib import Path

from watchdog.observers import Observer

from models import Base
from handlers import Handler

if __name__ == '__main__':
    Base.metadata.create_all()
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
