import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange


class VKBot:
    """
    Класс для взаимодействия с API VK и обработки входящих сообщений от пользователей.

    Args:
        vk_group_token (str): Токен группы VK для взаимодействия с API.
        server_confirmation_token (str): Токен для подтверждения сервера VK.
        secret_chat_token (str): Секретный токен для проверки сообщений от пользователей.

    Attributes:
        vk_group_token (str): Токен группы VK для взаимодействия с API.
        server_confirmation_token (str): Токен для подтверждения сервера VK.
        secret_chat_token (str): Секретный токен для проверки сообщений от пользователей.
        vk (vk_api.VkApiMethod): Объект для работы с методами VK API.
        longpoll (vk_api.longpoll.VkLongPoll): Объект для работы с Long Poll событиями VK.
    """

    def __init__(self, vk_group_token, server_confirmation_token, secret_chat_token):
        self.vk_group_token = vk_group_token
        self.server_confirmation_token = server_confirmation_token
        self.secret_chat_token = secret_chat_token

        # Создаем объект для работы с методами VK API
        self.vk = vk_api.VkApi(token=self.vk_group_token)
        # Создаем объект для работы с Long Poll событиями VK
        self.longpoll = VkLongPoll(self.vk)

    def send_message(self, user_id, message):
        """
        Отправляет сообщение пользователю VK.

        Args:
            user_id (int): Идентификатор пользователя VK.
            message (str): Текст сообщения.

        Returns:
            None
        """
        self.vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})

    def receive_messages(self):
        """
        Слушает Long Poll события и обрабатывает новые входящие сообщения от пользователей.

        Returns:
            None
        """
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                request = event.text
                user_id = event.user_id

                # Обработка входящего сообщения и отправка ответа здесь
                # При необходимости можно вызывать функции из других модулей

    def confirm_server(self, data):
        """
        Обрабатывает запрос от VK для подтверждения сервера.

        Args:
            data (dict): JSON-данные запроса от VK.

        Returns:
            str: Строка подтверждения сервера ("e448a003") при успешном запросе,
                 или пустая строка в случае другого типа запроса.
        """
        if data.get("type") == "confirmation" and data.get("group_id"):
            return "e448a003"  # Возвращаем строку подтверждения сервера
        return ""  # Возвращаем пустую строку, если это не запрос на подтверждение

    def handle_message(self, data):
        """
        Обрабатывает входящее сообщение от пользователя.

        Args:
            data (dict): JSON-данные запроса от VK.

        Returns:
            None
        """
        # Проверяем секретный токен во входящем сообщении
        if "secret" in data and data["secret"] == self.secret_chat_token:
            # Если токен совпадает, обрабатываем сообщение и отправляем ответ
            user_id = data.get("user_id")
            if user_id:
                self.send_message(user_id, "Вы отправили: " + data.get("text"))
        else:
            # Если токен не совпадает, игнорируем сообщение
            pass

    def start_listening(self):
        """
        Запускает прослушивание входящих сообщений VK.

        Returns:
            None
        """
        self.receive_messages()