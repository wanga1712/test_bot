from http.server import BaseHTTPRequestHandler
import json


class ConfirmationHandler(BaseHTTPRequestHandler):
    """
    Обработчик для подтверждения сервера VK и обработки входящих сообщений.

    Args:
        BaseHTTPRequestHandler (class): Базовый класс для обработки HTTP-запросов.

    Methods:
        do_POST(): Метод для обработки POST-запроса от VK.

    Attributes:
        bot (VKBot): Объект класса VKBot для взаимодействия с API VK и обработки запросов.
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
        """
        Обрабатывает POST-запрос от VK для подтверждения сервера или входящее сообщение от пользователя.

        Returns:
            None
        """
        # Получаем данные POST-запроса
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode("utf-8"))

        if "type" in data and data["type"] == "confirmation" and "group_id" in data:
            # Если это запрос на подтверждение сервера от VK, отправляем код подтверждения
            confirmation_response = self.bot.confirm_server(data)
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(confirmation_response.encode("utf-8"))
        else:
            # Если это входящее сообщение от пользователя, обрабатываем его
            self.bot.handle_message(data)
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Message received and processed!")  # Замените на вашу логику обработки сообщения

    #
    # except Exception as e:
    #     # Выводим сообщение об ошибке или логируем ее для отладки
    #     print("Ошибка во время обработки сообщения:", e)