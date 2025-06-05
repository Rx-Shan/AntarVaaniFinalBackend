import csv

def load_therapists(csv_path: str):
    with open(csv_path, encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return [dict(row) for row in reader]
