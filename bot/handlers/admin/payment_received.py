from aiogram import F, Bot, Router
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.clients.init_clients import storage_client
from bot.states import PaymentReceived
from bot.texts import PAYMENT_RECEIVED_MESSAGE, MAILING_CONFIRM_TEMPLATE
from bot.utils import make_keyboard, mailing, MailingTypes, AdminConfirmButtons

payment_received_router = Router()


@payment_received_router.message(
    PaymentReceived.confirm, F.text.in_([el.value for el in AdminConfirmButtons])
)
async def confirm(msg: Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    custom_type = user_data.get("custom_type")
    mailing_message = user_data.get("mailing_message")
    mailing_type = MailingTypes.specified.value

    await mailing(bot, mailing_type, custom_type, mailing_message)
    await msg.answer(
        text="Рассылка получения оплаты завершена", reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@payment_received_router.message(PaymentReceived.custom_type)
async def custom_type_chosen(msg: Message, state: FSMContext):
    custom_type = msg.text.lower()
    await state.update_data(custom_type=custom_type)

    mailing_message = PAYMENT_RECEIVED_MESSAGE.format(custom_type=custom_type)
    await state.update_data(mailing_message=mailing_message)
    await msg.answer(
        text=MAILING_CONFIRM_TEMPLATE.format(
            mailing_type=MailingTypes.specified.value,
            custom_type=custom_type,
            mailing_message=mailing_message,
        ),
        reply_markup=await make_keyboard([el.value for el in AdminConfirmButtons]),
    )
    await state.set_state(PaymentReceived.confirm)


@payment_received_router.message(StateFilter(None), Command("payment_received"))
async def payment_received_handler(msg: Message, state: FSMContext):
    await msg.answer(
        text="Выберите вид закупки:",
        reply_markup=await make_keyboard(
            await storage_client.get_custom_types_in_work()
        ),
    )
    await state.set_state(PaymentReceived.custom_type)
