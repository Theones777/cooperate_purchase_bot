from aiogram import F, Bot, Router
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.clients.init_clients import storage_client
from bot.states import Delay
from bot.texts import DELAY_MESSAGE
from bot.utils import make_keyboard, mailing, MailingTypes, AdminConfirmButtons

delay_router = Router()


@delay_router.message(
    Delay.confirm, F.text.in_([el.value for el in AdminConfirmButtons])
)
async def confirm(msg: Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    custom_type = user_data.get("custom_type")
    mailing_message = user_data.get("mailing_message")
    mailing_type = MailingTypes.specified.value

    await mailing(bot, mailing_type, custom_type, mailing_message)
    await msg.answer(
        text=f"Рассылка задержки заказа завершена", reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@delay_router.message(Delay.expected_date)
async def expected_date_inserted(msg: Message, state: FSMContext):
    user_data = await state.get_data()
    custom_type = user_data.get("custom_type")
    expected_date = msg.text.lower()
    mailing_message = DELAY_MESSAGE.format(
        custom_type=custom_type, expected_date=expected_date
    )
    await state.update_data(
        expected_date=expected_date, mailing_message=mailing_message
    )
    await msg.answer(
        text=f"Вы уверены, что хотите отправить данное сообщение?\n"
             f"Закупка - {custom_type}\n"
             f"Сообщение:\n{mailing_message}",
        reply_markup=await make_keyboard([el.value for el in AdminConfirmButtons])
    )
    await state.set_state(Delay.confirm)


@delay_router.message(Delay.custom_type)
async def custom_type_chosen(msg: Message, state: FSMContext):
    custom_type = msg.text.lower()
    await state.update_data(custom_type=custom_type)
    await msg.answer(
        text="Теперь, пожалуйста, введите дату предполагаемой поставки",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Delay.expected_date)


@delay_router.message(StateFilter(None), Command("delay_custom"))
async def delay_custom_handler(msg: Message, state: FSMContext):
    await msg.answer(
        text="Выберите вид закупки:",
        reply_markup=await make_keyboard(
            await storage_client.get_custom_types_in_work()
        ),
    )
    await state.set_state(Delay.custom_type)
