import vk_api
import time
import queue

class VKBot:
    def __init__(self, vk_group_token, server_confirmation_token, secret_chat_token):
        self.vk_group_token = vk_group_token
        self.server_confirmation_token = server_confirmation_token
        self.secret_chat_token = secret_chat_token
        self.vk_session = vk_api.VkApi(token=self.vk_group_token)
        self.vk = self.vk_session.get_api()
        self.last_processed_message_id = 0
        self.response_sent = False  # Flag to track whether a response has been sent
        self.received_message_ids = set()  # Set to store unique message identifiers
        self.sent_message_ids = set()  # Set to store message identifiers of messages sent by the bot

    def handle_message(self, data):
        if data.get("type") == "message_new":
            message = data["object"]["message"]
            if (
                message["conversation_message_id"] > self.last_processed_message_id
                and message["out"] == 0
                and not self.response_sent
            ):
                self.last_processed_message_id = message["conversation_message_id"]
                user_id = message["from_id"]
                text = message["text"]
                # Здесь обрабатываем сообщение от пользователя
                print(f"Received message from user_id {user_id}: {text}")

                # Here you can add code to process the message and send a response back to the user
                response_message = "This is a response message to the user"
                self.vk.messages.send(user_id=user_id, message=response_message, random_id=0)

                self.response_sent = True  # Set the flag to True after sending a response

                # Reset the response_sent flag before processing the next message
                self.reset_response_flag()

        elif data.get("type") == "message_reply":
            # Ignore message_reply events for messages sent by the bot itself
            pass

    def reset_response_flag(self):
        self.response_sent = False

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
            return "0b173ce7"  # Возвращаем строку подтверждения сервера
        return ""  # Возвращаем пустую строку, если это не запрос на подтверждение