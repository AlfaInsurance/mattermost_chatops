import json
import logging
import os
from threading import Thread
from flask import Flask
from ws_mm_app import WebSocketMattermostApp

app = Flask('mattermost-chat-ops-bot')

@app.route('/liveness')
@app.route('/readyness')
def getProbe():
    """
    Возвращает результат пробы для k8s
    """
    return "Healthy"

with app.app_context():
    # Настраиваем рабочую папку
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Добавляем логирование на основе файла
    with open('logging_config.json') as file:
        logging.config.dictConfig(json.load(file))
    logging.info("Logging configuration completed")

    # Стартуем WebSocket-приложение в отдельном потоке
    ws_thread = Thread(target=WebSocketMattermostApp.connect)
    ws_thread.start()

# Запускаем Flask-приложение при прямом вызове файла
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
