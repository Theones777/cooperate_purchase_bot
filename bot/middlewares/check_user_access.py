from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.utils import get_admin_ids


class CheckUserAccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if event.from_user.id not in await get_admin_ids():
            result = await handler(event, data)
            return result

        await event.answer("Вы слишком привилегированны!", show_alert=True)
        return
