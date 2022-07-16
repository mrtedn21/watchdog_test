import csv
import json
import re
from pathlib import Path

from dateutil.parser import parse
from sqlalchemy import MetaData
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

engine = create_engine('sqlite+pysqlite:///lite.db', future=True)
Base = declarative_base(engine)
metadata_obj = MetaData()


class Flight(Base):
    __tablename__ = 'flight'
    id = Column(Integer, primary_key=True)
    file_name = Column(String(256))
    flt = Column(Integer)
    depdate = Column(Date)
    dep = Column(String)


def from_any_date_to_iso(any_date: str):
    date_obj = parse(any_date)
    return date_obj.strftime('%Y-%m-%d')


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        with open(event.src_path, 'r') as f:
            file_name = Path(event.src_path).stem
            result_file = Path(event.src_path).parent.parent / 'Out' / f'{file_name}.json'
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

                person = {
                    'num': row[0],
                    'surname': row[1],
                    'firstname': row[2],
                    'bdate': from_any_date_to_iso(row[3]),
                }
                result_obj['prl'].append(person)

                with Session(engine) as session:
                    flight = Flight(
                        file_name=str(result_file),
                        flt=int(person['num']),
                        depdate=parse(parsed_file_name[0]),
                        dep=result_obj['dep'],
                    )
                    session.add(flight)
                    session.commit()

        with open(result_file, 'w') as f:
            f.write(json.dumps(result_obj))


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
