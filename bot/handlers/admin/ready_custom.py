from aiogram import F, Bot, Router
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.clients.init_clients import storage_client
from bot.states import Ready
from bot.texts import READY_MESSAGE, MAILING_CONFIRM_TEMPLATE
from bot.utils import make_keyboard, mailing, AdminConfirmButtons, MailingTypes

ready_router = Router()


@ready_router.message(
    Ready.confirm, F.text.in_([el.value for el in AdminConfirmButtons])
)
async def confirm(msg: Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    custom_type = user_data.get("custom_type")
    mailing_message = user_data.get("mailing_message")
    mailing_type = MailingTypes.specified.value

    await storage_client.set_custom_ready(custom_type)
    await mailing(bot, mailing_type, custom_type, mailing_message)
    await msg.answer(
        text="Рассылка готовности заказа завершена", reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@ready_router.message(
    Ready.custom_type,
)
async def custom_type_chosen(msg: Message, state: FSMContext):
    custom_type = msg.text.lower()
    mailing_message = READY_MESSAGE.format(custom_type=custom_type)
    await state.update_data(custom_type=custom_type, mailing_message=mailing_message)
    await msg.answer(
        text=MAILING_CONFIRM_TEMPLATE.format(
            mailing_type=MailingTypes.specified.value,
            custom_type=custom_type,
            mailing_message=mailing_message,
        ),
        reply_markup=await make_keyboard([el.value for el in AdminConfirmButtons]),
    )
    await state.set_state(Ready.confirm)


@ready_router.message(StateFilter(None), Command("ready_custom"))
async def ready_custom_handler(msg: Message, state: FSMContext):
    await msg.answer(
        text="Выберите вид закупки:",
        reply_markup=await make_keyboard(
            await storage_client.get_custom_types_in_work()
        ),
    )
    await state.set_state(Ready.custom_type)
