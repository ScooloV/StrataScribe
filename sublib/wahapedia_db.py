import json
import os
import csv
from datetime import datetime, timedelta

import requests

wahapedia_url = "https://wahapedia.ru/wh40k9ed/"
wahapedia_csv_list = ["Datasheets.csv", "Datasheets_stratagems.csv", "Factions.csv", "StratagemPhases.csv", "Stratagems.csv"]
wahapedia_path = os.path.abspath("./wahapedia")
file_list_path = os.path.abspath(os.path.join(wahapedia_path, "_file_list.json"))


def init_db():
    if not os.path.exists(wahapedia_path):
        os.mkdir(wahapedia_path)
        _create_file_list()
    for wahapedia_csv in wahapedia_csv_list:
        _check_csv(wahapedia_csv)


def _check_csv(csv_name):
    if not (os.path.exists(os.path.join(wahapedia_path, csv_name)) and _check_file_list(csv_name)):
        print(csv_name + " is bad, redownloading!")
        csv_path = _download_file(wahapedia_url + csv_name, wahapedia_path)
        _register_file_list(csv_name)
        print("Saved to " + csv_path)


def _check_file_list(csv_name):
    if not os.path.exists(file_list_path):
        print(file_list_path + " not exists, creating new")
        _create_file_list()

    with open(file_list_path, "r") as fl:
        current_file_list_json = json.load(fl)

    if csv_name in current_file_list_json:
        csv_time_delta = datetime.now() - datetime.fromisoformat(current_file_list_json[csv_name])
        print("File " + csv_name + " is updated [" + str(csv_time_delta) + "] ago")
        if csv_time_delta > timedelta(days=1):
            return False
        return True


def _create_file_list():
    empty_file_list = {}
    with open(file_list_path, "w") as fl:
        for wahapedia_csv in wahapedia_csv_list:
            empty_file_list[wahapedia_csv] = datetime.min.isoformat()
        json.dump(empty_file_list, fl)

def _register_file_list(csv_path):
    with open(file_list_path, "r") as fl:
        current_file_list_json = json.load(fl)

    current_file_list_json[csv_path] = str(datetime.now().isoformat())

    with open(file_list_path, "w") as fl:
        json.dump(current_file_list_json, fl)


def _download_file(file_url, folder_name):
    get_response = requests.get(file_url, stream=True)
    file_name = file_url.split("/")[-1]
    save_path = os.path.abspath(os.path.join(folder_name, file_name))
    with open(save_path, 'wb') as f:
        for chunk in get_response.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)

    return save_path

def get_dict_from_csv(csv_file_name):
    results = []
    csv_file_path = os.path.abspath(os.path.join(wahapedia_path, csv_file_name))
    with open(csv_file_path, 'r', encoding='ascii', errors='ignore') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='|', quoting=csv.QUOTE_NONE)
        for row in reader:
            results.append(row)

    return results
