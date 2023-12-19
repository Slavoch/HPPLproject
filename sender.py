import requests
import json

# Function to generate a JSON message based on provided chart data and optional parameters.
def generate_message(x, y, title=None, x_label=None, y_label=None, legend=None):
    args = locals()  # Capture the local variables (arguments)
    message = dict()  # Initialize an empty dictionary to build the message
    # Iterate through the arguments and add them to the message if they are not None
    for arg in args.items():
        if arg[1] is not None:
            message[arg[0]] = arg[1]
    json_msg = json.dumps(message)  # Convert the message dictionary to a JSON string
    return json_msg  # Return the JSON string

# Function to send data to a server using POST request.
def send_to_data_server(data, path):
    url = f"http://localhost:9023/{path}"  # Construct the URL using the provided path
    # Send a POST request to the specified URL with the given data and return the response
    return requests.post(url, data=data)

if __name__ == "__main__":
    # Main block to test the functions
    for _ in range(10):  # Loop 10 times
        # Generate a JSON message with predefined data and a title
        json_message = generate_message(x=[1, 1], y=[2, 424], title="lol")
        # Send the generated message to the data server under the path "lol"
        send_to_data_server(json_message, "lol")