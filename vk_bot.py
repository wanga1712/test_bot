class VKBot:
    def __init__(self, vk_group_token, server_confirmation_token, secret_chat_token):
        self.vk_group_token = vk_group_token
        self.server_confirmation_token = server_confirmation_token
        self.secret_chat_token = secret_chat_token

    def handle_message(self, data):
        """
        Обрабатывает сообщение от пользователя.

        Args:
            data (dict): JSON-данные сообщения от VK.

        Returns:
            None
        """
        if data.get("type") == "message_new":
            user_id = data["object"]["message"]["from_id"]
            message = data["object"]["message"]["text"]
            # Здесь обрабатываем сообщение от пользователя
            print(f"Received message from user_id {user_id}: {message}")

        elif data.get("type") == "message_reply":
            user_id = data["object"]["from_id"]
            message = data["object"]["text"]
            # Здесь обрабатываем ответное сообщение
            print(f"Received message reply from user_id {user_id}: {message}")

    @staticmethod
    def confirm_server(data):
        """
        Обрабатывает запрос от VK для подтверждения сервера.

        Args:
            data (dict): JSON-данные запроса от VK.

        Returns:
            str: Строка подтверждения сервера при успешном запросе,
                 или пустая строка в случае другого типа запроса.
        """
        if data.get("type") == "confirmation" and data.get("group_id"):
            return "e448a003"  # Возвращаем строку подтверждения сервера
        return ""  # Возвращаем пустую строку, если это не запрос на подтверждение
