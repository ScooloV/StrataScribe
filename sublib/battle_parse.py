import os
import pathlib
import zipfile
from datetime import datetime, timedelta

import xmltodict
from lxml import html

from sublib import wahapedia_db, wh40k_lists

# Absolute path of the battlescribe folder
battlescribe_folder = os.path.abspath("./battlescribe")

# Global dictionaries to store the data read from csv files
_ros_dict = {}
_datasheets_dict = {}
_datasheets_stratagems_dict = {}
_factions_dict = {}
_stratagem_phases_dict = {}
_stratagems_dict = {}

# Global lists to store the data extracted from the battlescribe file
_roster_list = []
_empty_stratagems_list = []
_full_stratagems_list = []

# WebUI options dictionary
_request_options = {}


def init_parse():
    """
    Initialize the parse by reading all csv files to dictionary format and creating the battlescribe folder if it does not exist
    """
    global _datasheets_dict, _datasheets_stratagems_dict, _factions_dict, _stratagem_phases_dict, _stratagems_dict
    # reading all csv file to dictionary format
    _datasheets_dict = wahapedia_db.get_dict_from_csv("Datasheets.csv")
    _datasheets_stratagems_dict = wahapedia_db.get_dict_from_csv("Datasheets_stratagems.csv")
    _factions_dict = wahapedia_db.get_dict_from_csv("Factions.csv")
    _stratagem_phases_dict = wahapedia_db.get_dict_from_csv("StratagemPhases.csv")
    _stratagems_dict = wahapedia_db.get_dict_from_csv("Stratagems.csv")

    # folder for battlescribe files should exist
    if not os.path.exists(battlescribe_folder):
        os.mkdir(battlescribe_folder)

    # filtering all stratagems which doesn't have any unit requirements
    _find_empty_stratagems()


# request_options are coming from Web UI and has several options
def parse_battlescribe(battlescribe_file_name, request_options):
    """
    Parse the battlescribe file and returns the result in the form of a list of dictionaries and a list of lists
    """
    global _full_stratagems_list, _request_options

    if wahapedia_db.init_db() is True:
        init_parse()

    _full_stratagems_list = []
    wh_empty_stratagems = []
    wh_core_stratagems = []
    _request_options = request_options

    _read_ros_file(battlescribe_file_name)
    _prepare_roster_list()

    wh_faction = _find_faction()
    wh_units = _find_units(wh_faction)

    if _request_options.get("show_empty") == "on":
        wh_empty_stratagems = _filter_empty_stratagems(wh_faction)

    if _request_options.get("show_core") == "on":
        wh_core_stratagems = _filter_core_stratagems()

    if _request_options.get("dont_show_before") == "on":
        wh40k_lists.ignore_phases_list.append("Before battle")

    wh_stratagems = _find_stratagems(wh_units)

    result_phase = []
    result_units = []

    for id in range(0, len(wh_faction)):
        current_empty_stratagems = []
        if len(wh_empty_stratagems) != 0:
            current_empty_stratagems = wh_empty_stratagems[id]

        current_id_phase = _prepare_stratagems_phase(wh_stratagems[id] + current_empty_stratagems + wh_core_stratagems, wh_units[id], wh_faction[id])
        currend_id_units = _prepare_stratagems_units(wh_stratagems[id] + current_empty_stratagems + wh_core_stratagems, wh_units[id], wh_faction[id])
        result_phase.append(current_id_phase)
        result_units.append(currend_id_units)

    _delete_old_files()

    result_phase_sorted = []
    for phase_elem in result_phase:
        phase_elem_sorted = {i: phase_elem[i] for i in sorted(phase_elem, key=lambda j: wh40k_lists.phases_list.index(j))}
        result_phase_sorted.append(phase_elem_sorted)

    return result_phase_sorted, result_units, _get_full_stratagems_list()


def _get_full_stratagems_list():
    global _full_stratagems_list
    sorted_stratagems_list = list(_full_stratagems_list)
    sorted_stratagems_list.sort()

    full_list = []
    for stratagem_id in sorted_stratagems_list:
        clean_stratagem = _clean_full_stratagem(_get_stratagem_from_id(stratagem_id, clean_stratagem=True))
        full_list.append(clean_stratagem)

    return full_list


def _clean_full_stratagem(stratagem_dict):
    result_stratagem = dict(stratagem_dict)
    del result_stratagem["source_id"]
    del result_stratagem[""]
    result_stratagem["description"] = _clean_html(result_stratagem["description"])

    return result_stratagem


def _read_ros_file(file_name):
    global _ros_dict
    ros_file_name = file_name
    file_path = os.path.join(battlescribe_folder, file_name)
    if pathlib.Path(file_path).suffix == ".rosz":
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            rosz_packed_filename = zip_ref.infolist()[0].filename
            battlescribe_tmp = os.path.join(battlescribe_folder, "tmp")
            ros_file_name = file_name[:-1]

            zip_ref.extractall(battlescribe_tmp)
            ros_file_path = os.path.join(battlescribe_folder, ros_file_name)
            if os.path.exists(ros_file_path):
                os.remove(ros_file_path)
            os.rename(os.path.join(battlescribe_tmp, rosz_packed_filename), ros_file_path)

    _ros_dict = _get_dict_from_xml(ros_file_name)


# if roster has several forces, that it is multidetachment army and _roster_list has more elements
def _prepare_roster_list():
    global _ros_dict, _roster_list
    _roster_list = []
    if isinstance(_ros_dict['roster']['forces']['force'], list):
        for roster_force in _ros_dict["roster"]["forces"]["force"]:
            _roster_list.append(roster_force)
    else:
        _roster_list.append(_ros_dict["roster"]["forces"]["force"])


def _find_faction():
    result_faction = []
    is_subfaction = False

    for roster_elem in _roster_list:
        catalogueName = roster_elem["@catalogueName"]
        catalogueName_clean = _get_faction_name(catalogueName)

        for faction in _factions_dict:
            if faction["name"] in catalogueName_clean or catalogueName_clean in faction["name"]:
                force_faction = faction
                if faction["is_subfaction"] == "true":
                    is_subfaction = True

        subfaction_names = []
        if not is_subfaction:
            for selection in roster_elem["selections"]["selection"]:
                if selection["@name"] in wh40k_lists.subfaction_types:
                    if selection.get("selections") is not None:
                        if type(selection["selections"]["selection"]) == list:
                            for element in selection["selections"]["selection"]:
                                subfaction_names.append(element["@name"].replace("'", ""))
                        else:
                            subfaction_names.append(selection["selections"]["selection"]["@name"].replace("'", ""))
                        for faction in _factions_dict:
                            for subfaction_name in subfaction_names:
                                if faction["name"] in subfaction_name \
                                        or subfaction_name in faction["name"] \
                                        or wh40k_lists.subfaction_rename_dict.get(subfaction_name) == faction["name"]:
                                    force_faction = faction
                                    break

        result_faction.append(force_faction)
    return result_faction


def _find_units(faction_ids):
    total_units = []

    for id in range(0, len(faction_ids)):
        result_units = []
        faction_id = faction_ids[id]
        roster_force = _roster_list[id]
        if roster_force.get("selections") is not None:
            for unit in roster_force["selections"]["selection"]:
                if unit["@name"] not in wh40k_lists.selection_non_unit_types:
                    for datasheet in _datasheets_dict:
                        if faction_id["id"] == datasheet["faction_id"] or faction_id["parent_id"] == datasheet["faction_id"]:
                            if _compare_unit_names(datasheet["name"], unit["@name"]):
                                if datasheet not in result_units:
                                    result_units.append(datasheet)
        total_units.append(result_units)

    return total_units


def _find_empty_stratagems():
    global _empty_stratagems_list
    empty_stratagems_full_list = []
    for stratagem in _stratagems_dict:
        stratagem_found = False
        stratagem_id = stratagem["id"]
        if _stratagem_is_valid(stratagem_id):
            for datasheet_stratagem in _datasheets_stratagems_dict:
                if stratagem_id == datasheet_stratagem["stratagem_id"]:
                    stratagem_found = True
                    break

            if not stratagem_found:
                empty_stratagems_full_list.append(stratagem)

    _empty_stratagems_list = empty_stratagems_full_list


def _filter_empty_stratagems(faction_ids):
    global _empty_stratagems_list
    stratagems_list = []
    for faction_id in faction_ids:
        result_list = []
        for empty_stratagem in _empty_stratagems_list:
            if faction_id["id"] == empty_stratagem["subfaction_id"] and faction_id["id"] != "" \
                    or faction_id["parent_id"] == empty_stratagem["faction_id"] and faction_id["parent_id"] != "":
                result_list.append({"datasheet_id": "", "stratagem_id": empty_stratagem["id"]})
        stratagems_list.append(result_list)

    return stratagems_list


def _filter_core_stratagems():
    global _empty_stratagems_list
    result_list = []
    for empty_stratagem in _empty_stratagems_list:
        if empty_stratagem["type"] == "Core Stratagem":
            result_list.append({"datasheet_id": "", "stratagem_id": empty_stratagem["id"]})

    return result_list


def _find_stratagems(units_ids):
    stratagems_list = []
    for units_id in units_ids:
        result_stratagems = []
        for unit_id in units_id:
            for datasheets_stratagem in _datasheets_stratagems_dict:
                if datasheets_stratagem["datasheet_id"] == unit_id["id"]:
                    result_stratagems.append(datasheets_stratagem)
        stratagems_list.append(result_stratagems)

    return stratagems_list


def _prepare_stratagems_phase(stratagems_id, units_id, faction_id):
    global _full_stratagems_list
    result_stratagems_phase = {}
    for stratagem_id in stratagems_id:
        if _stratagem_is_valid(stratagem_id["stratagem_id"]):
            for stratagem_phase in _stratagem_phases_dict:
                if stratagem_phase["stratagem_id"] == stratagem_id["stratagem_id"]:
                    full_stratagem = _get_stratagem_from_id(stratagem_id["stratagem_id"], stratagems_id, units_id)
                    if full_stratagem["subfaction_id"] == "" \
                            or full_stratagem["subfaction_id"] == full_stratagem["faction_id"] \
                            or full_stratagem["subfaction_id"] == faction_id["id"]:

                        if stratagem_phase["phase"] not in result_stratagems_phase:
                            # result_stratagems_phase[stratagem_phase["phase"]] = [stratagem_id["stratagem_id"]]
                            result_stratagems_phase[stratagem_phase["phase"]] = [full_stratagem["name"]]
                            if full_stratagem["id"] not in _full_stratagems_list:
                                _full_stratagems_list.append(full_stratagem["id"])
                        else:
                            if full_stratagem["name"] not in result_stratagems_phase[stratagem_phase["phase"]]:
                                # result_stratagems_phase[stratagem_phase["phase"]].append(stratagem_id["stratagem_id"])
                                result_stratagems_phase[stratagem_phase["phase"]].append(full_stratagem["name"])
                                if full_stratagem["id"] not in _full_stratagems_list:
                                    _full_stratagems_list.append(full_stratagem["id"])

    return result_stratagems_phase


def _prepare_stratagems_units(stratagems_id, units_id, faction_id):
    global _full_stratagems_list
    results_stratagems_units = {}
    # filling results
    for unit_id in units_id:
        unit_id_name = unit_id["name"]
        if _request_options.get("show_units") == "on":
            unit_id_name = "[" + str(units_id.index(unit_id) + 1) + "] " + unit_id_name
        results_stratagems_units[unit_id_name] = []

    # assigning stratagems to units it belongs
    for stratagem_id in stratagems_id:
        if _stratagem_is_valid(stratagem_id["stratagem_id"]):
            for unit_id in units_id:
                if stratagem_id["datasheet_id"] == unit_id["id"]:
                    full_stratagem = _get_stratagem_from_id(stratagem_id["stratagem_id"])
                    if full_stratagem["subfaction_id"] == "" \
                            or full_stratagem["subfaction_id"] == full_stratagem["faction_id"] \
                            or full_stratagem["subfaction_id"] == faction_id["id"]:

                        unit_id_name = unit_id["name"]
                        if _request_options.get("show_units") == "on":
                            unit_id_name = "[" + str(units_id.index(unit_id) + 1) + "] " + unit_id_name

                        # results_stratagems_units[unit_id["name"]].append(stratagem_id["stratagem_id"])
                        results_stratagems_units[unit_id_name].append(full_stratagem["name"])
                        if full_stratagem["id"] not in _full_stratagems_list:
                            _full_stratagems_list.append(full_stratagem["id"])

    return results_stratagems_units


def _get_stratagem_from_id(stratagem_id, stratagems_list=None, units_list=None, clean_stratagem=None):
    for stratagem in _stratagems_dict:
        if stratagem["id"] == stratagem_id:
            if _request_options is not None and clean_stratagem is not True:
                if _request_options.get("show_units") == "on" and units_list is not None:
                    result_stratagem = dict(stratagem)
                    for stratagem_elem in stratagems_list:
                        if stratagem_elem["stratagem_id"] == stratagem_id:
                            for unit_elem in units_list:
                                if unit_elem["id"] == stratagem_elem["datasheet_id"]:
                                    result_stratagem["name"] += " [" + str(units_list.index(unit_elem) + 1) + "]"
                    return result_stratagem
                elif _request_options.get("show_phases") == "on" and units_list is None:
                    result_stratagem = dict(stratagem)
                    for stratagem_phase in _stratagem_phases_dict:
                        if stratagem_phase["stratagem_id"] == stratagem_id:
                            result_stratagem["name"] += " [" + _get_first_letters(stratagem_phase["phase"]) + "]"
                    return result_stratagem

            return stratagem


def _stratagem_is_valid(stratagem_id):
    full_stratagem = _get_stratagem_from_id(stratagem_id)
    stratagem_type = full_stratagem["type"]

    for invalid_stratagem_type in wh40k_lists.invalid_stratagems_type:
        if invalid_stratagem_type in stratagem_type:
            return False

    if _request_options.get("show_renown") != "on":
        for army_of_renown_name in wh40k_lists.army_of_renown_list:
            if army_of_renown_name in full_stratagem["type"]:
                return False

    if _get_stratagem_phase(stratagem_id) in wh40k_lists.ignore_phases_list:
        return False

    if stratagem_type != "Stratagem":
        for valid_stratagem_type in wh40k_lists.valid_stratagems_type:
            if valid_stratagem_type in stratagem_type:
                return True

    return False


def _get_stratagem_phase(stratagem_id):
    for stratagem_phase in _stratagem_phases_dict:
        if stratagem_phase["stratagem_id"] == stratagem_id:
            return stratagem_phase["phase"]


def _get_faction_name(catalogue_name):
    catalogue_array = _remove_symbol(catalogue_name.split(" - "), "'")
    if catalogue_array[-1] == "Craftworlds":
        return catalogue_array[0]

    return catalogue_array[-1]


# compares battlescribe and wahapedia names according to rename dictionary
def _compare_unit_names(wahapedia_name, battlescribe_name):
    clean_battlescribe_name = battlescribe_name.replace("'", "")
    if clean_battlescribe_name in wh40k_lists.unit_rename_dict:
        if wh40k_lists.unit_rename_dict[clean_battlescribe_name] == wahapedia_name:
            return True

    if wahapedia_name == clean_battlescribe_name:
        return True

    return False


# --- NON-Stratagem stuff ---
def _get_first_letters(line):
    words = line.split()
    letters = [word[0] for word in words]
    return "".join(letters)


def _clean_html(html_string):
    # return html_string
    return str(html.fromstring(html_string).text_content())


def _delete_old_files():
    file_list = os.listdir(battlescribe_folder)
    for single_file in file_list:
        single_file_path = os.path.join(battlescribe_folder, single_file)
        creation_time = datetime.fromtimestamp(os.path.getctime(single_file_path))
        file_time_delta = datetime.now() - creation_time
        if file_time_delta > timedelta(hours=1):
            try:
                os.remove(single_file_path)
                print(single_file + " deleted")
            except:
                print("Can't delete " + single_file)


def _get_dict_from_xml(xml_file_name):
    xml_file_path = os.path.join(battlescribe_folder, xml_file_name)
    with open(xml_file_path, errors='ignore') as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
        return data_dict


def _remove_symbol(arr, symbol):
    return [word.replace(symbol, '') for word in arr]
