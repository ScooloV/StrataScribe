import csv
import json
import os
import time
from datetime import datetime, timedelta

import requests

# URL for the Wahapedia website
wahapedia_url = "https://wahapedia.ru/wh40k9ed/"

# List of all CSV files to be downloaded from the website
wahapedia_csv_list = ["Datasheets.csv", "Datasheets_stratagems.csv", "Factions.csv", "StratagemPhases.csv", "Stratagems.csv", "Last_update.csv"]

# Path to the local directory where the CSV files will be saved
wahapedia_path = os.path.abspath("./wahapedia")

# Path to the file that keeps track of the last time the CSV files were updated
file_list_path = os.path.abspath(os.path.join(wahapedia_path, "_file_list.json"))


def init_db():
    """
    Initializes the local database by checking if the CSV files need to be updated.
    If the local directory or the file list do not exist, they will be created.
    If a CSV file does not exist or is older than 1 day, it will be downloaded from the website.
    :return: True if any of the CSV files were updated, False otherwise
    """
    check_csv_update = False
    if not os.path.exists(wahapedia_path):
        os.mkdir(wahapedia_path)
        _create_file_list()

    if _wahapedia_has_update():
        for wahapedia_csv in wahapedia_csv_list:
            check_result = _check_csv(wahapedia_csv)
            if check_result is True:
                check_csv_update = True

    return check_csv_update


def _wahapedia_has_update():
    """
    Checks if the Wahapedia website has any new updates by comparing the last_update field from the Last_update.csv file.
    If the file does not exist or the last_update field has changed, it will download the file.
    :return: True if the website has new updates, False otherwise
    """
    last_update_path = os.path.join(wahapedia_path, "Last_update.csv")

    if not os.path.exists(last_update_path):
        print("Last_update.csv doesn't exists")
        return True

    last_update_dict_old = get_dict_from_csv(last_update_path)
    _check_csv("Last_update.csv")
    last_update_dict_new = get_dict_from_csv(last_update_path)

    if (last_update_dict_old[0]["last_update"]) != (last_update_dict_new[0]["last_update"]):
        print("Wahapedia has new updates")
        return True
    return False


def _check_csv(csv_name):
    """
    Checks if the specified CSV file needs to be updated by comparing its last update time with the file list.
    If the file does not exist or is older than 1 day, it will be downloaded from the website and the file list will be updated.
:param csv_name: the name of the CSV file to be checked
:return: True if the file was updated, False otherwise
"""

    csv_updated = False
    if not (os.path.exists(os.path.join(wahapedia_path, csv_name)) and _check_file_list(csv_name)):
        print(csv_name + " is bad, redownloading!")
        csv_path = _download_file(wahapedia_url + csv_name, wahapedia_path)
        _register_file_list(csv_name)
        print("Saved to " + csv_path)
        csv_updated = True

    return csv_updated


def _check_file_list(csv_name):
    """
    Checks if the specified CSV file is in the file list and if it was updated in the last 1 day.
    If the file list does not exist, it will be created.
    :param csv_name: the name of the CSV file to be checked
    :return: True if the file is in the file list and was updated in the last 1 day, False otherwise
    """
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
    """
    Creates the file list with the current time for all the CSV files in the wahapedia_csv_list.
    """
    empty_file_list = {}
    with open(file_list_path, "w") as fl:
        for wahapedia_csv in wahapedia_csv_list:
            empty_file_list[wahapedia_csv] = datetime.min.isoformat()
        json.dump(empty_file_list, fl)


def _register_file_list(csv_path):
    """
    Registers the specified CSV file in the file list with the current time.
    :param csv_path: the path of the CSV file to be registered
    """
    with open(file_list_path, "r") as fl:
        current_file_list_json = json.load(fl)

    current_file_list_json[csv_path] = str(datetime.now().isoformat())

    with open(file_list_path, "w") as fl:
        json.dump(current_file_list_json, fl)


def _download_file(file_url, folder_name):
    """
    Downloads a file from a specified url and saves it to a specified folder.
    :param file_url: the url of the file to be downloaded
    :param folder_name: the folder where the file will be saved
    :return: the path where the file was saved
    """
    file_name = file_url.split("/")[-1]
    save_path = os.path.abspath(os.path.join(folder_name, file_name))

    file_downloaded = False

    # Keep trying to download the file until it is successfully downloaded
    while not file_downloaded:
        get_response = requests.get(file_url, stream=True)
        # Open the file and write the content in chunks
        with open(save_path, 'wb') as f:
            for chunk in get_response.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        file_size = os.stat(save_path).st_size
        # Check if the file size is smaller than 2048 bytes, which could indicate that anti-spam is working
        if file_size < 2048 and file_name != "Last_update.csv":
            print("Anti Spam is working. Waiting for 5 second to try again.")
            time.sleep(5)
        else:
            file_downloaded = True

    return save_path



def get_dict_from_csv(csv_path):
    """
    Converts a CSV file to a list of dictionaries
    :param csv_path: the path of the CSV file to be converted
    :return: a list of dictionaries
    """
    results = []
    csv_file_path = os.path.abspath(os.path.join(wahapedia_path, csv_path))
    with open(csv_file_path, 'r', encoding='ascii', errors='ignore') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='|', quoting=csv.QUOTE_NONE)
        for row in reader:
            results.append(row)

    return results
