import http.client
import json
import logging
import logging.config
import time
import websocket

from utils.incoming_post_handler import IncomingPostHandler, bot_mm_tag
from utils.kaiten_helper import KaitenHelper
from utils.mm_helper import MmHelper


class WebSocketMattermostApp:
    """
    Приложение, слушающее Mattermost через WebSocket
    """

    mm_ws_headers = dict()
    """
    Словарь заголовков для WebSocket-запросов к API Mattermost
    """

    connection: websocket.WebSocketApp
    """
    Соединение с WebSocket
    """

    def configure():
        """
        Конфигурирует приложение из файла config.json
        """

        with open('config.json') as file:
            global config
            config = json.load(file)
        logging.info("Configuration files loaded")

        # Клиент к API Mattermost
        MmHelper.client = http.client.HTTPSConnection(
            config["mattermost"]["host"])
        mm_auth = f"Bearer {config['mattermost']['token']}"
        MmHelper.headers["Authorization"] = mm_auth
        MmHelper.headers["Content-Type"] = "application/json"

        # Заголовки для подключения к Mattermost через WebSocket
        WebSocketMattermostApp.mm_ws_headers["Authorization"] = mm_auth

        # Адрес для подключения к Mattermost через WebSocket
        global mm_ws_url
        mm_ws_url = f"wss://{config['mattermost']['host']}/api/v4/websocket"

        # Клиент к API Kaiten
        KaitenHelper.client = http.client.HTTPSConnection(
            config["kaiten"]["host"])

        KaitenHelper.headers["Authorization"] = f"Bearer {config['kaiten']['token']}"
        KaitenHelper.headers["Content-Type"] = "application/json"

        IncomingPostHandler.users_of_bot = config['mattermost_allowed_users']

        logging.info("Configuration completed")

    def connect():
        """
        Подключается к WebSocket
        """

        WebSocketMattermostApp.configure()
        while (True):
            WebSocketMattermostApp.connection = websocket.WebSocketApp(mm_ws_url,
                                                                   header=WebSocketMattermostApp.mm_ws_headers,
                                                                   on_open=WebSocketMattermostApp.ws_on_open,
                                                                   on_message=WebSocketMattermostApp.ws_on_message,
                                                                   on_error=WebSocketMattermostApp.ws_on_error,
                                                                   on_close=WebSocketMattermostApp.ws_on_close)
            WebSocketMattermostApp.connection.run_forever(reconnect=60)
            sleepInterval = 3600.0
            logging.warn(f"Starting sleep for {sleepInterval}s")
            time.sleep(sleepInterval)

    def ws_on_message(ws, message):
        """
        Обрабатывает поступающие сообщения

        Parameters
        ----------
        ws : websocket.WebSocketApp
            Websocket-приложение
        message : str
            Полученное json-сообщение
        """
        msg_obj = json.loads(message)

        # Отбираем входящие сообщения с упоминанием my_tag
        if msg_obj["event"] == "posted" and bot_mm_tag in msg_obj["data"]["post"]:
            post_obj = json.loads(msg_obj["data"]["post"])

            # Ищем пользователя в списке разрешенных
            found_user = next(
                (mm_user for mm_user in config["mattermost_allowed_users"]
                 if mm_user["id"] == post_obj["user_id"]),
                None)
            if found_user != None:
                IncomingPostHandler.handle(post_obj)

    def ws_on_error(ws, error):
        """
        Выполняет действия при ошибке

        Parameters
        ----------
        ws : websocket.WebSocketApp
            Websocket-приложение
        error : str
            Текст ошибки
        """
        logging.error(f"Error: {error}")

    def ws_on_close(ws, close_status_code, close_msg):
        """
        Выполняет действия при закрытии соединения

        Parameters
        ----------
        ws : websocket.WebSocketApp
            Websocket-приложение
        close_status_code : str
            Код закрытия
        close_msg : str
            Текст сообщения о закрытии
        """
        logging.info(
            f"Connection closed: {close_status_code} | {close_msg}")

    def ws_on_open(ws):
        """
        Выполняет действия при открытии соединения

        Parameters
        ----------
        ws : websocket.WebSocketApp
            Websocket-приложение
        """
        logging.info("Connection opened")


# При запуске файла напрямую соединяется автоматически
if __name__ == "__main__":
    WebSocketMattermostApp.connect()
