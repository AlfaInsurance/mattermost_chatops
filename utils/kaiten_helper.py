import http.client
import json
import re


class KaitenHelper:

    """
    Помощник для обращения к API Kaiten
    """

    headers = dict()
    """
    Словарь заголовков для запросов к API Kaiten
    """

    client: http.client.HTTPSConnection = None
    """
    Клиент к API Kaiten
    """

    def create_kaiten_card(message, creator_id):
        """
        Создает карточку в Kaiten

        Parameters
        ----------
        message : str
            Текст сообщения для парсинга задачи
        creator_id : str
            ИД создателя задачи
        """

        # Параметры по умолчанию
        board_id = 1  # ИД Доски
        lane_id = 2  # ИД Дорожки на Доске
        type_id = 26  # ИД типа карточки
        properties = {}

        # Текст задачи
        double_quotes_title_regex = re.compile(
            r'"(.+)"',
            flags=re.I | re.M)
        single_quotes_title_regex = re.compile(
            r'\'(.+)\'',
            flags=re.I | re.M)
        task_title_regex = re.compile(
            r'(задач|таск|kaiten|кайтен).*? (.+)',
            flags=re.I | re.M)
        title_search = double_quotes_title_regex.search(message)
        if title_search == None:
            title_search = single_quotes_title_regex.search(message)
        if title_search == None:
            title_search = task_title_regex.search(message)
        if title_search == None or len(title_search.groups()) == 0:
            return None
        title = title_search.groups()[-1]

        # Меняем часть значений для техдолговых задач
        tech_debt_regex = re.compile(
            r'(в тех.*долг|тех.*долг.+(задач|таск))',
            flags=re.I | re.M)
        if tech_debt_regex.search(message):
            # Параметры для задач Технического долга
            board_id = 4  # Доска: Технический долг
            lane_id = 2  # Дорожка: Важные
            type_id = 7  # Тип для технического долга

        body = json.dumps({
            "title": title,
            "board_id": board_id,
            "lane_id": lane_id,
            "owner_id": creator_id,
            "type_id": type_id,
            "properties": properties
        })

        KaitenHelper.client.request("POST", "/api/latest/cards",
                                    body, KaitenHelper.headers)
        response = KaitenHelper.client.getresponse()
        response_obj = json.loads(response.read().decode())
        KaitenHelper.client.close()
        return response_obj["id"]
