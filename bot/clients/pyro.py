from pyrogram import Client
from aiogram.types import Message
import asyncio

from bot.log import logger
from config import Config


class PyroClient:
    def __init__(self):
        self.client = Client(
            Config.TG_SESSION_NAME,
            Config.API_ID,
            Config.API_HASH,
            session_string=Config.SESSION_STRING,
        )

    async def _get_link_message(self, sent_message: Message):
        async for msg in self.client.get_chat_history(
                Config.PAYMENT_BOT_USERNAME, limit=Config.TG_PAYMENT_BOT_MESSAGES_LIMIT
        ):
            if msg.from_user.is_bot and msg.id == sent_message.id + 1 and "http" in msg.text:
                return msg.text

    async def get_payment_link(self, custom_cost: int):
        response_text = None
        time = 0

        try:
            sent_message = await self.client.send_message(Config.PAYMENT_BOT_USERNAME, custom_cost)

            while not response_text and time <= Config.TG_PAYMENT_BOT_TIMEOUT:
                response_text = await self._get_link_message(sent_message)
                time+=1
                await asyncio.sleep(1)
            else:
                if not response_text:
                    response_text = (
                        "Ошибка получения ссылки на оплату, "
                        "попробуйте позже либо свяжитесь с администратором"
                    )
                    logger.error(f"get_payment_link error от {Config.PAYMENT_BOT_USERNAME}\n "
                                 f"Ошибка получения ответа")

        except Exception as e:
            response_text = "Ошибка получения ссылки на оплату, попробуйте позже либо свяжитесь с администратором"
            logger.error(f"Unexpected error от {Config.PAYMENT_BOT_USERNAME}\n {e}")

        return response_text
