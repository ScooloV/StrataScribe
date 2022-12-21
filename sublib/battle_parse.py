import os
import pathlib
import zipfile

from lxml import html

import xmltodict

from sublib import wahapedia_db

subfaction_types = ["Order", "Forge World", "Brotherhood", "Noble Household", "Chapter",
                    "Allegiance", "Dread Household", "Legion", "Plague Company",
                    "Great Cult", "Craftworld", "Kabal", "Wych Cult", "Haemonculus Coven", "Cult", "League", "Dynasty", "Clan", "Sept", "Hive Fleet"]

selection_non_unit_types = ["**Chapter Selector**", "Game Type", "Detachment Command Cost"]

battlescribe_folder = os.path.abspath("./battlescribe")

_ros_dict = {}
_datasheets_dict = {}
_datasheets_stratagems_dict = {}
_factions_dict = {}
_stratagem_phases_dict = {}
_stratagems_dict = {}
_full_stratagems_list = []


def init_parse():
    global _datasheets_dict, _datasheets_stratagems_dict, _factions_dict, _stratagem_phases_dict, _stratagems_dict
    _datasheets_dict = wahapedia_db.get_dict_from_csv("Datasheets.csv")
    _datasheets_stratagems_dict = wahapedia_db.get_dict_from_csv("Datasheets_stratagems.csv")
    _factions_dict = wahapedia_db.get_dict_from_csv("Factions.csv")
    _stratagem_phases_dict = wahapedia_db.get_dict_from_csv("StratagemPhases.csv")
    _stratagems_dict = wahapedia_db.get_dict_from_csv("Stratagems.csv")

    if not os.path.exists(battlescribe_folder):
        os.mkdir(battlescribe_folder)


def parse_battlescribe(battlescribe_file_name):
    global _full_stratagems_list
    _full_stratagems_list = []

    _read_ros_file(battlescribe_file_name)
    wh_faction = _find_faction()
    wh_units = _find_units(wh_faction)
    wh_stratagems = _find_stratagems(wh_units)
    result_phase = _prepare_stratagems_phase(wh_stratagems, wh_faction)
    result_units = _prepare_stratagems_units(wh_stratagems, wh_units, wh_faction)
    return result_phase, result_units, _get_full_stratagems_list()


def _get_full_stratagems_list():
    global _full_stratagems_list
    full_list = []
    for stratagem_id in _full_stratagems_list:
        clean_stratagem = _clean_full_stratagem(_get_stratagem_from_id(stratagem_id)) 
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


def _find_faction():
    result_faction = []
    is_subfaction = False
    catalogueName = _ros_dict["roster"]["forces"]["force"]["@catalogueName"]
    catalogueName_list = catalogueName.split(" - ")

    for faction in _factions_dict:
        if faction["name"] in catalogueName_list[-1] or catalogueName_list[-1] in faction["name"]:
            result_faction = faction
            if faction["is_subfaction"] == "true":
                is_subfaction = True

    if not is_subfaction:
        for selection in _ros_dict["roster"]["forces"]["force"]["selections"]["selection"]:
            if selection["@name"] in subfaction_types:
                subfaction_name = selection["selections"]["selection"]["@name"]
                for faction in _factions_dict:
                    if faction["name"] in subfaction_name or subfaction_name in faction["name"]:
                        result_faction = faction
                        break

    return result_faction


def _find_units(faction_id):
    result_units = []

    for unit in _ros_dict["roster"]["forces"]["force"]["selections"]["selection"]:
        if unit["@name"] not in selection_non_unit_types:
            for datasheet in _datasheets_dict:
                if faction_id["id"] == datasheet["faction_id"] or faction_id["parent_id"] == datasheet["faction_id"]:
                    if datasheet["name"] == unit["@name"]:
                        if datasheet not in result_units:
                            result_units.append(datasheet)

    return result_units


def _find_stratagems(units_id):
    result_stratagems = []
    for unit_id in units_id:
        for datasheets_stratagem in _datasheets_stratagems_dict:
            if datasheets_stratagem["datasheet_id"] == unit_id["id"]:
                result_stratagems.append(datasheets_stratagem)

    return result_stratagems


def _prepare_stratagems_phase(stratagems_id, faction_id):
    global _full_stratagems_list
    result_stratagems_phase = {}
    for stratagem_id in stratagems_id:
        for stratagem_phase in _stratagem_phases_dict:
            if stratagem_phase["stratagem_id"] == stratagem_id["stratagem_id"]:
                full_stratagem = _get_stratagem_from_id(stratagem_id["stratagem_id"])
                if full_stratagem["subfaction_id"] == "" or full_stratagem["subfaction_id"] == faction_id["id"] or full_stratagem["subfaction_id"] == faction_id["parent_id"]:
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
    for unit_id in units_id:
        for stratagem_id in stratagems_id:
            if stratagem_id["datasheet_id"] == unit_id["id"]:
                full_stratagem = _get_stratagem_from_id(stratagem_id["stratagem_id"])
                if full_stratagem["subfaction_id"] == "" or full_stratagem["subfaction_id"] == faction_id["id"] or full_stratagem["subfaction_id"] == faction_id["parent_id"]:
                    if unit_id["name"] not in results_stratagems_units:
                        # results_stratagems_units[unit_id["name"]] = [stratagem_id["stratagem_id"]]
                        results_stratagems_units[unit_id["name"]] = [full_stratagem["name"]]
                        if full_stratagem["id"] not in _full_stratagems_list:
                            _full_stratagems_list.append(full_stratagem["id"])
                    else:
                        # results_stratagems_units[unit_id["name"]].append(stratagem_id["stratagem_id"])
                        results_stratagems_units[unit_id["name"]].append(full_stratagem["name"])
                        if full_stratagem["id"] not in _full_stratagems_list:
                            _full_stratagems_list.append(full_stratagem["id"])
    return results_stratagems_units


def _get_stratagem_from_id(stratagem_id):
    for stratagem in _stratagems_dict:
        if stratagem["id"] == stratagem_id:
            return stratagem

def _clean_html(html_string):
    return str(html.fromstring(html_string).text_content())
def _get_dict_from_xml(xml_file_name):
    xml_file_path = os.path.join(battlescribe_folder, xml_file_name)
    with open(xml_file_path) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
        return data_dict
