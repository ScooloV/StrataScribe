from json2html import json2html

def convert_to_table(json_dict):
    table_attributes = 'style="margin-top:10px; margin-left:10px; margin-bottom:10px;" border="2"'
    return json2html.convert(json=json_dict, table_attributes=table_attributes)
