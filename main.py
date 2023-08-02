import os
from dotenv import load_dotenv
from vk_bot import VKBot
from http.server import HTTPServer
from app import ConfirmationHandler
import threading

if __name__ == "__main__":
    """
    Главный файл для запуска сервера подтверждения VK и VKBot.

    Returns:
        None
    """
    try:
        load_dotenv(dotenv_path=r'C:\Users\wangr\PycharmProjects\pythonProject8\keys.env')  # Загрузка переменных окружения из файла .env
        vk_group_token = os.getenv("CHAT_TOKEN")
        server_confirmation_token = os.getenv("VK_API_TOKEN")
        secret_chat_token = os.getenv("SECRET_CHAT_TOKEN")

        # Создаем объект класса VKBot для взаимодействия с API VK и обработки сообщений
        bot = VKBot(vk_group_token, server_confirmation_token, secret_chat_token)

        # Запуск простого HTTP-сервера для обработки запроса подтверждения сервера VK
        server_address = ("", 5000)
        httpd = HTTPServer(server_address, lambda *args, **kwargs: ConfirmationHandler(bot=bot, *args, **kwargs))
        print("Сервер запущен.")

        # Запускаем HTTP-сервер для обработки запросов от VK в отдельном потоке
        httpd_thread = threading.Thread(target=httpd.serve_forever)
        httpd_thread.start()

        # Ожидаем завершения работы HTTP-сервера
        httpd_thread.join()

        # Этот код будет выполнен только после остановки HTTP-сервера, что произойдет только если его остановят вручную.
        print("Сервер остановлен.")

    except Exception as e:
        print("Произошла ошибка при загрузке переменных окружения:", e)