from aiogram import F, Bot, Router
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.clients.init_clients import storage_client
from bot.states import Mailing
from bot.utils import make_keyboard, mailing, MailingTypes, AdminConfirmButtons

mailing_router = Router()


@mailing_router.message(
    Mailing.confirm, F.text.in_([el.value for el in AdminConfirmButtons])
)
async def confirm(msg: Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    mailing_type = user_data.get("mailing_type")
    custom_type = user_data.get("custom_type")
    mailing_message = user_data.get("mailing_message")

    await mailing(bot, mailing_type, custom_type, mailing_message)

    await msg.answer(text=f"Рассылка завершена", reply_markup=ReplyKeyboardRemove())
    await state.clear()


@mailing_router.message(Mailing.mailing_message)
async def mailing_message_inserted(msg: Message, state: FSMContext):
    mailing_message = msg.text
    user_data = await state.get_data()
    mailing_type = user_data.get("mailing_type")
    custom_type = user_data.get("custom_type")

    await state.update_data(mailing_message=mailing_message)
    await msg.answer(
        text=f"Вы уверены, что хотите отправить данное сообщение?\n"
             f"Тип рассылки - {mailing_type}\n"
             f"Закупка - {custom_type}\n"
             f"Сообщение:\n{mailing_message}",
        reply_markup=await make_keyboard([el.value for el in AdminConfirmButtons])
    )
    await state.set_state(Mailing.confirm)


@mailing_router.message(Mailing.custom_type)
async def custom_type_chosen(msg: Message, state: FSMContext):
    custom_type = msg.text
    await state.update_data(custom_type=custom_type)
    await msg.answer(
        text="Теперь, пожалуйста, введите сообщение для отправки",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Mailing.mailing_message)


@mailing_router.message(
    Mailing.mailing_type, F.text.in_([el.value for el in MailingTypes])
)
async def mailing_type_chosen(msg: Message, state: FSMContext):
    chosen_mailing_type = msg.text
    await state.update_data(mailing_type=chosen_mailing_type)
    if chosen_mailing_type == MailingTypes.specified.value:
        await msg.answer(
            text="Теперь, пожалуйста, выберите вид закупки:",
            reply_markup=await make_keyboard(
                await storage_client.get_custom_types_in_work()
            ),
        )
        await state.set_state(Mailing.custom_type)
    else:
        await msg.answer(
            text="Теперь, пожалуйста, введите сообщение для отправки",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(Mailing.mailing_message)


@mailing_router.message(StateFilter(None), Command("message_mailing"))
async def message_mailing_handler(msg: Message, state: FSMContext):
    await msg.answer(
        text="Выберите тип рассылки:",
        reply_markup=await make_keyboard([el.value for el in MailingTypes]),
    )
    await state.set_state(Mailing.mailing_type)
