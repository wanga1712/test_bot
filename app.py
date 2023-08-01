from http.server import BaseHTTPRequestHandler
import json


class ConfirmationHandler(BaseHTTPRequestHandler):
    """
    Обработчик для подтверждения сервера VK.

    Args:
        BaseHTTPRequestHandler (class): Базовый класс для обработки HTTP-запросов.

    Methods:
        do_POST(): Метод для обработки POST-запроса от VK.

    Attributes:
        bot (VKBot): Объект класса VKBot для взаимодействия с API VK и обработки запроса.
    """

    def __init__(self, *args, **kwargs):
        """
        Инициализация обработчика.

        Args:
            *args: Позиционные аргументы базового класса.
            **kwargs: Ключевые аргументы базового класса.

        Returns:
            None
        """
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

            # Send a single response to the VK server after processing the user message
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Message received and processed!")

            # Reset the response_sent flag after sending the response
            self.bot.reset_response_flag()
