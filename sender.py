import requests
import json


def generate_message(x, y, title=None, x_label=None, y_label=None, legend=None):
    args = locals()
    message = dict()
    for arg in args.items():
        if arg[1] is not None:
            message[arg[0]] = arg[1]
    json_msg = json.dumps(message)
    return json_msg


def send_to_data_server(msg, data_name):
    url = f"http://localhost:9023/{data_name}"
    response = requests.post(url, data=msg)
    return response
