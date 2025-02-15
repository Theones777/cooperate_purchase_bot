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

    async def check_user_payment(self, qr_number: str):
        time = 0
        try:
            while time <= Config.TG_PAYMENT_BOT_TIMEOUT:
                async for msg in self.client.get_chat_history(
                        Config.PAYMENT_BOT_USERNAME, limit=Config.TG_PAYMENT_BOT_MESSAGES_LIMIT
                ):
                    # and msg.reply_to_message_id == qr_message_id
                    if msg.from_user.is_bot and msg.text and qr_number in msg.text and "Оплачено по QR-коду" in msg.text:
                        return True
                time += 1
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Unexpected error check_user_payment от {Config.PAYMENT_BOT_USERNAME}\n {e}")

        return False

    @staticmethod
    async def _reformat_payment_message(response_text: str):
        if "Ошибка" in response_text:
            return response_text

        response_text_split = response_text.split("\n")
        qr_number = response_text_split[1].split(" ")[-1]
        qr_link = response_text_split[-1].split(" ")[-1]
        return qr_number, qr_link

    async def _get_link_message(self, sent_message: Message):
        async for msg in self.client.get_chat_history(
                Config.PAYMENT_BOT_USERNAME, limit=Config.TG_PAYMENT_BOT_MESSAGES_LIMIT
        ):
            if msg.from_user.is_bot and msg.id == sent_message.id + 1 and msg.caption and "http" in msg.caption:
                return msg.caption

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
                        "пожалуйста свяжитесь с администратором"
                    )
                    logger.error(f"get_payment_link error от {Config.PAYMENT_BOT_USERNAME}\n "
                                 f"Ошибка получения ответа")

        except Exception as e:
            response_text = "Ошибка получения ссылки на оплату, пожалуйста свяжитесь с администратором"
            logger.error(f"Unexpected error от {Config.PAYMENT_BOT_USERNAME}\n {e}")

        return await self._reformat_payment_message(response_text)
