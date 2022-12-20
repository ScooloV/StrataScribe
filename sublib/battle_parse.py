import pathlib
import zipfile
import os
import json

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


def init_parse():
    global _datasheets_dict, _datasheets_stratagems_dict, _factions_dict, _stratagem_phases_dict, _stratagems_dict
    _datasheets_dict = wahapedia_db.get_dict_from_csv("Datasheets.csv")
    _datasheets_stratagems_dict = wahapedia_db.get_dict_from_csv("Datasheets_stratagems.csv")
    _factions_dict = wahapedia_db.get_dict_from_csv("Factions.csv")
    _stratagem_phases_dict = wahapedia_db.get_dict_from_csv("StratagemPhases.csv")
    _stratagems_dict = wahapedia_db.get_dict_from_csv("Stratagems.csv")


def parse_battlescribe(battlescribe_file_name):
    _read_ros_file(battlescribe_file_name)
    wh_faction = _find_faction()
    wh_units = _find_units(wh_faction)
    wh_stratagems = _find_stratagems(wh_units)
    result_phase = _prepare_stratagems_phase(wh_stratagems, wh_faction)
    result_units = _prepare_stratagems_units(wh_stratagems, wh_units, wh_faction)
    return result_phase, result_units


def _read_ros_file(file_name):
    global _ros_dict
    ros_file_name = file_name
    file_path = os.path.join(battlescribe_folder, file_name)
    if pathlib.Path(file_path).suffix == ".rosz":
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(battlescribe_folder)
        ros_file_name = file_name[:-1]

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
    result_stratagems_phase = {}
    for stratagem_id in stratagems_id:
        for stratagem_phase in _stratagem_phases_dict:
            if stratagem_phase["stratagem_id"] == stratagem_id["stratagem_id"]:
                full_stratagem = _get_stratagem_from_id(stratagem_id["stratagem_id"])
                if full_stratagem["subfaction_id"] == "" or full_stratagem["subfaction_id"] == faction_id["id"]:
                    if stratagem_phase["phase"] not in result_stratagems_phase:
                        # result_stratagems_phase[stratagem_phase["phase"]] = [stratagem_id["stratagem_id"]]
                        result_stratagems_phase[stratagem_phase["phase"]] = [full_stratagem["name"]]
                    else:
                        if full_stratagem["name"] not in result_stratagems_phase[stratagem_phase["phase"]]:
                            # result_stratagems_phase[stratagem_phase["phase"]].append(stratagem_id["stratagem_id"])
                            result_stratagems_phase[stratagem_phase["phase"]].append(full_stratagem["name"])

    return result_stratagems_phase


def _prepare_stratagems_units(stratagems_id, units_id, faction_id):
    results_stratagems_units = {}
    for unit_id in units_id:
        for stratagem_id in stratagems_id:
            if stratagem_id["datasheet_id"] == unit_id["id"]:
                full_stratagem = _get_stratagem_from_id(stratagem_id["stratagem_id"])
                if full_stratagem["subfaction_id"] == "" or full_stratagem["subfaction_id"] == faction_id["id"]:
                    if unit_id["name"] not in results_stratagems_units:
                        # results_stratagems_units[unit_id["name"]] = [stratagem_id["stratagem_id"]]
                        results_stratagems_units[unit_id["name"]] = [full_stratagem["name"]]
                    else:
                        # results_stratagems_units[unit_id["name"]].append(stratagem_id["stratagem_id"])
                        results_stratagems_units[unit_id["name"]].append(full_stratagem["name"])

    return results_stratagems_units


def _get_stratagem_from_id(stratagem_id):
    for stratagem in _stratagems_dict:
        if stratagem["id"] == stratagem_id:
            return stratagem


def _get_dict_from_xml(xml_file_name):
    xml_file_path = os.path.join(battlescribe_folder, xml_file_name)
    with open(xml_file_path) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
        return data_dict
