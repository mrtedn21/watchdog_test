import csv
import json
import shutil
import re
from pathlib import Path

from dateutil.parser import parse
from sqlalchemy.orm import Session
from watchdog.events import FileSystemEventHandler

from models import Flight
from models import engine


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        CsvFileHandler(event.src_path).handle()


class CsvFileHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = ''
        self.result_file = ''
        self.flight_dict = {}

    def handle(self):
        """ main function that handles file and
        save all data to db and other files"""

        try:
            self._parse_file_path()
            parsed_file_name = self._parse_file_name()
            self._initial_flight_dict(parsed_file_name)
            self._fill_flight_dict_with_person_data()
            self._save_all_flights_to_db()
            self._save_json_file()
        except BaseException as e:
            self._move_source_file('Err')
        else:
            self._move_source_file('Ok')

    def _parse_file_path(self):
        self.file_name = Path(self.file_path).stem
        self.result_file = Path(
            self.file_path
        ).parent.parent / 'Out' / f'{self.file_name}.json'

    def _parse_file_name(self):
        return re.fullmatch(
            '(\d{8})_(\d+)_(.+)',
            self.file_name
        ).groups()

    def _initial_flight_dict(self, parsed_file_name):
        self.flight_dict = {
            'flt': int(parsed_file_name[1]),
            'date': from_any_date_to_iso(parsed_file_name[0]),
            'dep': parsed_file_name[2],
            'prl': [],
        }

    def _csv_run(self, file):
        csv_obj = csv.reader(file, delimiter=';')
        for row in csv_obj:
            if not row:
                continue
            yield row

    def _make_person_dict(self, csv_row):
        return {
            'num': csv_row[0],
            'surname': csv_row[1],
            'firstname': csv_row[2],
            'bdate': from_any_date_to_iso(csv_row[3]),
        }

    def _save_flight_to_db(self, person):
        with Session(engine) as session:
            flight = Flight(
                file_name=str(self.result_file),
                flt=int(person['num']),
                depdate=parse(self.flight_dict['date']),
                dep=self.flight_dict['dep'],
            )
            session.add(flight)
            session.commit()

    def _fill_flight_dict_with_person_data(self):
        with open(self.file_path, 'r') as file:
            for csv_row in self._csv_run(file):
                person = self._make_person_dict(csv_row)
                self.flight_dict['prl'].append(person)

    def _save_all_flights_to_db(self):
        for person in self.flight_dict['prl']:
            self._save_flight_to_db(person)

    def _save_json_file(self):
        with open(self.result_file, 'w') as f:
            f.write(json.dumps(self.flight_dict))

    def _move_source_file(self, directory_name):
        parent_dir = Path(self.file_path).parent.parent

        shutil.move(
            self.file_path,
            parent_dir / directory_name / self.file_name
        )


def from_any_date_to_iso(any_date: str):
    date_obj = parse(any_date)
    return date_obj.strftime('%Y-%m-%d')
