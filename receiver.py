from flask import Flask, request, jsonify
import json
import numpy as np
import server


def run_data_server(data_base):
    app = Flask("Dash app data server")

    def generate_empy_slot():
        slot = dict(
            x=[],
            y=[],
        )
        return slot

    def generate_slot_in_db(name):
        slot = generate_empy_slot()
        data_base[name] = slot

    @app.route("/<slot_name>", methods=["POST"])
    def hello(slot_name):
        if slot_name not in data_base.keys():
            generate_slot_in_db(slot_name)

        data = json.loads(request.data)
        db_slot = data_base[slot_name]
        db_slot["x"] = np.hstack([db_slot["x"], data["x"]])
        db_slot["y"] = np.hstack([db_slot["y"], data["y"]])
        data_base[slot_name] = db_slot
        return "1"

    app.run(debug=True)


if __name__ == "__main__":
    data_base = {}
    app = Flask("Dash app data server")

    def generate_empy_slot():
        slot = dict(
            x=[],
            y=[],
            legend="None",
            title="None",
            active_in=[],
            is_changed=True,
        )
        return slot

    def generate_slot_in_db(name):
        slot = generate_empy_slot()
        data_base[name] = slot

    @app.route("/<slot_name>", methods=["POST"])
    def hello(slot_name):
        if slot_name not in data_base.keys():
            generate_slot_in_db(slot_name)

        data = json.loads(request.data)
        db_slot = data_base[slot_name]
        db_slot["x"] = np.hstack([db_slot["x"], data["x"]])
        db_slot["y"] = np.hstack([db_slot["y"], data["y"]])
        db_slot["is_changed"] = True

        if "title" in data:
            db_slot["title"] = data["title"]

        data_base[slot_name] = db_slot
        # print(data_base)
        return "1"

    server.run_UI_server(app, data_base)
