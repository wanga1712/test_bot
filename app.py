from http.server import BaseHTTPRequestHandler
import json


class ConfirmationHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.bot = kwargs.pop('bot', None)
        super().__init__(*args, **kwargs)

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode("utf-8"))

        print("Received data from VK:", data)  # Debug print to see the received data

        if "type" in data and data["type"] == "confirmation" and "group_id" in data:
            confirmation_response = self.bot.confirm_server(data)
            print("Sending confirmation response:", confirmation_response)  # Add log to see the confirmation response
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()  # Add this line to end the headers
            self.wfile.write(confirmation_response.encode("utf-8"))
        elif "type" in data and data["type"] == "message_new":
            # Process the user message
            self.bot.handle_message(data)

            # Respond to the VK server with "OK" for message_new events
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            # Respond to other events with "OK"
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
