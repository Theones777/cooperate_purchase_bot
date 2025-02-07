from aiogram import Router
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.clients.init_clients import storage_client
from bot.states import Sync
from bot.utils import sync_db_to_gs, make_keyboard

sync_router = Router()


@sync_router.message(Sync.custom_type)
async def custom_type_chosen(msg: Message, state: FSMContext):
    custom_type = msg.text.lower()
    if await sync_db_to_gs(custom_type):
        message = "Синхронизация базы данных с Гугл-таблицей завершена"
    else:
        message = "Ошибка синхронизации"
    await msg.answer(
        text=message,
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.clear()


@sync_router.message(StateFilter(None), Command("sync"))
async def sync_handler(msg: Message, state: FSMContext):
    await msg.answer(
        text="Выберите вид закупки:",
        reply_markup=await make_keyboard(
            await storage_client.get_custom_types_in_work()
        ),
    )
    await state.set_state(Sync.custom_type)
