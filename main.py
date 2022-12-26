import os.path
import pathlib
import uuid

from flask import Flask, render_template, request

from sublib import wahapedia_db, battle_parse, prepare_html

app = Flask(__name__)

upload_directory = os.path.abspath("./battlescribe")


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        file_ext = pathlib.Path(f.filename).suffix

        if file_ext == ".ros" or file_ext == ".rosz":
            random_filename = str(uuid.uuid4()) + file_ext
            f.save(os.path.join(upload_directory, random_filename))
            json_phase, json_units, json_stratagems = battle_parse.parse_battlescribe(random_filename, request.form)
            html_phase = prepare_html.convert_to_table(json_phase)
            html_units = prepare_html.convert_to_table(json_units)
            html_stratagems = prepare_html.convert_to_stratagem_list(json_stratagems)
        return render_template("report.html", html_phase=html_phase, html_units=html_units, html_stratagems=html_stratagems)

    if request.method == 'GET':
        return render_template("upload.html")


if __name__ == '__main__':
    wahapedia_db.init_db()
    battle_parse.init_parse()
    app.run(debug=False)
