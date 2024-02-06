import re

from utils.kaiten_helper import KaitenHelper
from utils.mm_helper import MmHelper

bot_mm_tag = "@bot"
"""
Тэг бота в Mattermost
"""

create_kaiten_card_regex = re.compile(
    r'(созда|завед|нов[ау]|полож).+(задач|таск|kaiten|кайтен)', flags=re.I | re.M)
"""
Регулярное выражение для идентификации сценария создания карточки в Kaiten
"""

create_kaiten_card_help = f"```\n{bot_mm_tag} Создай задачу \"Сделать бизнесу фичу\"\n{bot_mm_tag} Заведи таску в техдолге 'Обновить все фреймворки на последнюю версию'\n{bot_mm_tag} Новая задачка Распознавание печатей на документах\n```"

"""
Регулярное выражение для идентификации сценария создания карточки в Kaiten
"""


class IncomingPostHandler:
    """
    Обработчик входящих сообщений
    """

    users_of_bot = {}
    """
    Пользователи бота Mattermost
    """

    def handle(post_obj):
        """
        Обрабатывает входящее сообщение
        """
        reply = ""
        if create_kaiten_card_regex.search(post_obj['message']):
            reply = IncomingPostHandler.handle_create_kaiten_card(post_obj)
        else:
            reply = IncomingPostHandler.handle_help()

        mm_root_id = post_obj["id"] if post_obj["root_id"] == "" else post_obj["root_id"]
        MmHelper.post_to_mm(reply, post_obj["channel_id"], mm_root_id)

    def handle_create_kaiten_card(post_obj):
        """
        Обрабатывает сценарий создания карточки в Kaiten
        """
        kaiten_creator_id: int = next(
            (user["kaiten_id"]
             for user in IncomingPostHandler.users_of_bot if user["id"] == post_obj["user_id"]),
            None)
        created_id = KaitenHelper.create_kaiten_card(
            post_obj['message'], kaiten_creator_id)
        if created_id == None:
            return f":( Не смог определить текст задачи\n:bulb: Попробуйте так:\n\n{create_kaiten_card_help}"
        else:
            return f":white_check_mark: Создал задачу {created_id}\n:earth_africa: [Открыть в Kaiten](https://kaiten.mycompany.com/space/36/card/{created_id})"

    def handle_help():
        """
        Обрабатывает сценарий приветствия / просьбы о помощи
        """
        return f"Привет! Не смог распознать вашу команду. Я пока что умею вот что:\n:kaiten: **Создавать задачки в Кайтен**\n{create_kaiten_card_help}"
