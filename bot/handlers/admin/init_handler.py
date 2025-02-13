from aiogram import Router
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.handlers.admin.delay_custom import delay_router
from bot.handlers.admin.mailing import mailing_router
from bot.handlers.admin.payment_received import payment_received_router
from bot.handlers.admin.ready_custom import ready_router
from bot.handlers.admin.start_custom import start_custom_router
from bot.handlers.admin.sync_custom import sync_router
from bot.middlewares.check_admin_access import CheckAdminAccessMiddleware

admin_router = Router()
admin_router.include_routers(
    delay_router,
    payment_received_router,
    mailing_router,
    ready_router,
    start_custom_router,
    sync_router,
)
admin_router.message.middleware(CheckAdminAccessMiddleware())


@admin_router.message(StateFilter("*"), Command(commands=["cancel"]))
async def cancel_handler(msg: Message, state: FSMContext):
    await state.set_data({})
    await state.clear()
    await msg.answer("Возврат к началу", reply_markup=ReplyKeyboardRemove())
