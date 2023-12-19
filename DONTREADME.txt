from flask import Flask, request, jsonify
import json
import numpy as np
import server
def run_data_server(data_base):
    app = Flask("Dash app data server")

    def generate_empy_slot():
        slot = dict(
            X=[],
            Y=[],
        )
        return slot

    def generate_slot_in_db(name):
        slot = generate_empy_slot()
        DataBase[name] = slot

    @app.route("/<slot_name>", methods=["POST"])
    def hello(slot_name):
        if slot_name not in DataBase.keys():
            generate_slot_in_db(slot_name)

        data = json.loads(request.data)
        db_slot = DataBase[slot_name]
        db_slot[" X "] = np.hstack([db_slot[" X "], data[" X "]])
        db_slot[" Y "] = np.hstack([db_slot[" Y "], data[" Y "]])
        DataBase[slot_name] = db_slot
        return "1"

    app.run(debug=True)

if __name__ == "__main__":
    DataBase = {}
    app = Flask("Dash app data server")

    def generate_empy_slot():
        slot = dict(
            X=[],
            Y=[],
            legend="None",
            title="None",
            active_in=[],
        )
        return slot

    def generate_slot_in_db(name):
        slot = generate_empy_slot()
        DataBase[name] = slot

    @app.route("/<slot_name>", methods=["POST"])
    def hello(slot_name):
        if slot_name not in DataBase.keys():
            generate_slot_in_db(slot_name)

        data = json.loads(request.data)
        db_slot = DataBase[slot_name]
        db_slot[" X "] = np.hstack([db_slot[" X "], data[" X "]])
        db_slot[" Y "] = np.hstack([db_slot[" Y "], data[" Y "]])
        DataBase[slot_name] = db_slot
        return "1"

    server.run_UI_server(app, DataBase)