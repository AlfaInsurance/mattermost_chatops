import http.client
import json


class MmHelper:
    """
    Помощник для обращения к API Mattermost
    """

    headers = dict()
    """
    Словарь заголовков для запросов к API Mattermost
    """

    client: http.client.HTTPSConnection = None
    """
    Клиент к API Mattermost
    """

    def post_to_mm(message, channel_id, root_id="", props={}):
        """
        Отправляет в Mattermost сообщение

        Parameters
        ----------
        message : str
            Текст сообщения
        channel_id : str
            ИД канала в Mattermost
        root_id : str, optional
            ИД корневого сообщения, если нужно ответить в треде
        props : object, optional
            Дополнительные свойства сообщения
        """
        body = json.dumps({
            "channel_id": channel_id,
            "root_id": root_id,
            "message": message,
            "props": props
        })
        MmHelper.client.request("POST", "/api/v4/posts", body, MmHelper.headers)
        MmHelper.client.close()
