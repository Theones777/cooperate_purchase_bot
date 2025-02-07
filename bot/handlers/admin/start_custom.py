from aiogram import F, Bot, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.clients.init_clients import gs_client, storage_client
from bot.states import Start
from bot.utils import make_keyboard, AdminConfirmButtons, MailingTypes, mailing
from config import Config

start_custom_router = Router()


@start_custom_router.message(
    Start.confirm, F.text.in_([el.value for el in AdminConfirmButtons])
)
async def confirm(msg: Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    custom_type = user_data.get("custom_type")
    mailing_message = user_data.get("mailing_message")
    application_date = user_data.get("application_date")
    mailing_type = MailingTypes.massive.value

    create_date = await gs_client.make_custom_worksheet(custom_type)
    await storage_client.save_custom_type_to_work(
        custom_type=custom_type, application_date=application_date, create_date=create_date
    )
    buttons = [
        f"{Config.MAKE_CUSTOM_PREFIX}{custom_type}"
        for custom_type in await storage_client.get_custom_types_in_work()
    ]

    await mailing(bot, mailing_type, custom_type, mailing_message, buttons)
    await msg.answer(
        text=f"Рассылка начала закупки завершена", reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@start_custom_router.message(
    Start.expected_date,
)
async def expected_date_inserted(msg: Message, state: FSMContext):
    user_data = await state.get_data()
    custom_type = user_data.get("custom_type")
    expected_date = msg.text.lower()
    mailing_message, application_date = await gs_client.make_start_custom_message(
        custom_type, expected_date
    )
    await state.update_data(
        expected_date=expected_date,
        mailing_message=mailing_message,
        application_date=application_date,
    )
    await msg.answer(
        text=f"Вы уверены, что хотите отправить данное сообщение?\n"
             f"Закупка - {custom_type}\n"
             f"Сообщение:\n{mailing_message}",
        reply_markup=await make_keyboard([el.value for el in AdminConfirmButtons])
    )
    await state.set_state(Start.confirm)


@start_custom_router.message(Start.custom_type)
async def custom_type_chosen(msg: Message, state: FSMContext):
    custom_type = msg.text.lower()
    await state.update_data(custom_type=custom_type)
    await msg.answer(
        text="Теперь, пожалуйста, введите дату поставки",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(Start.expected_date)


@start_custom_router.message(StateFilter(None), Command("start_custom"))
async def start_custom_handler(msg: Message, state: FSMContext):
    await msg.answer(
        text="Выберите вид закупки:",
        reply_markup=await make_keyboard(await gs_client.get_all_custom_types()),
    )
    await state.set_state(Start.custom_type)
