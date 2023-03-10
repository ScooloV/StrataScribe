import string

from json2html import json2html

table_attributes = 'class="table table-bordered table-striped w-auto print-friendly"; '

stratagem_template = '<div class="stratWrapper_CS BreakInsideAvoid">' \
                     '<div class="$stratagem_class"><span>$stratagem_name</span><span>${stratagem_cp_cost}CP</span></div>' \
                     '<div class="stratFaction_CS">$stratagem_type</div>' \
                     '<p class="ShowFluff stratLegend2">$stratagem_legend</p>' \
                     '<div class="stratText_CS">$stratagem_description </div>' \
                     '</div>'


# def convert_to_table(json_dict):
#     return json2html.convert(json=json_dict, table_attributes=table_attributes)


def convert_to_table(json_list):
    result_html = ""
    for json_elem in json_list:
        result_html += json2html.convert(json=json_elem, table_attributes=table_attributes) + " "

    return result_html


def convert_to_stratagem_list(json_list):
    result_html = ""
    for json_elem in json_list:
        json_template = string.Template(stratagem_template)
        stratagem_class = "stratName_9k "
        if "Battle Tactic Stratagem" in json_elem["type"]:
            stratagem_class += " stratBattleTactic"
        elif "Strategic Ploy Stratagem" in json_elem["type"]:
            stratagem_class += " stratStrategicPloy"
        elif "Epic Deed Stratagem" in json_elem["type"]:
            stratagem_class += " stratEpicDeed"
        elif "Requisition Stratagem" in json_elem["type"]:
            stratagem_class += " stratRequisition"
        elif "Wargear Stratagem" in json_elem["type"]:
            stratagem_class += " stratWargear"
        elif "Core Stratagem" in json_elem["type"]:
            stratagem_class = "stratName_CS"
        else:
            stratagem_class = "stratName_WSP"
        clean_template = json_template.substitute(stratagem_name=json_elem["name"],
                                                  stratagem_cp_cost=json_elem["cp_cost"],
                                                  stratagem_class=stratagem_class,
                                                  stratagem_type=json_elem["type"],
                                                  stratagem_legend=json_elem["legend"],
                                                  stratagem_description=json_elem["description"])

        result_html += clean_template

    return result_html
