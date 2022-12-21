from json2html import json2html

table_attributes = 'style="margin-top:10px; margin-left:10px; margin-bottom:10px;" border="2"'

def convert_to_table(json_dict):
    return json2html.convert(json=json_dict, table_attributes=table_attributes)

def convert_list_to_tables(json_list):
    result_html = ""
    for json_elem in json_list:
        result_html += json2html.convert(json=json_elem, table_attributes=table_attributes) + " "

    return result_html