from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.clients.init_clients import storage_client
from bot.states import User
from bot.utils import (
    make_keyboard,
    UserConfirmButtons,
    check_user_custom_format,
    check_custom_application_date,
)
from config import Config

user_router = Router()


@user_router.message(User.confirm, F.text.in_([el.value for el in UserConfirmButtons]))
async def confirm(msg: Message, state: FSMContext):
    if msg.text == UserConfirmButtons.sure.value:
        user_data = await state.get_data()
        custom_type = user_data.get("custom_type")
        user_custom = user_data.get("user_custom")
        user_purchase = {msg.from_user.id: user_custom}
        await storage_client.save_user_to_working_custom_type(custom_type, user_purchase)
        message = "Заказ принят, ожидайте сообщение об оплате"

    else:
        message = "Заказ отменен"

    await state.clear()
    await msg.answer(
        text=message,
        reply_markup=await make_keyboard(
            [
                f"{Config.MAKE_CUSTOM_PREFIX}{custom_type}"
                for custom_type in await storage_client.get_custom_types_in_work()
            ]
        ),
    )


@user_router.message(User.user_custom)
async def custom_inserted(msg: Message, state: FSMContext):
    user_custom = msg.text.lower()
    user_data = await state.get_data()
    custom_type = user_data.get("custom_type")
    if user_custom := await check_user_custom_format(user_custom, custom_type):
        await state.update_data(user_custom=user_custom)
        await msg.answer(
            text=f"Вы уверены, что хотите сделать заказ?\n"
                 f"Закупка - <b>{custom_type}</b>\n"
                 f"Состав: \n{user_custom}",
            reply_markup=await make_keyboard([el.value for el in UserConfirmButtons]))
        await state.set_state(User.confirm)
    else:
        await msg.answer(
            text="Неверный формат данных для закупки, пожалуйста введите согласно образцу",
            reply_markup=ReplyKeyboardRemove(),
        )


@user_router.message(StateFilter(None))
async def message_handler(msg: Message, state: FSMContext):
    custom_type = msg.text.replace(Config.MAKE_CUSTOM_PREFIX, "").lower()
    if custom_type in await storage_client.get_custom_types_in_work():
        flag_application_date = await check_custom_application_date(custom_type)
        flag_user_in_working_custom = await storage_client.check_user_in_working_custom(custom_type, msg.from_user.id)

        if flag_application_date and not flag_user_in_working_custom:
            await state.update_data(custom_type=custom_type)
            await msg.answer(
                text="Введите, пожалуйста Ваш заказ в формате:\n"
                     "<i>Товар1 - количество\n"
                     "Товар2 - количество ... </i>\n",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.set_state(User.user_custom)
        elif not flag_application_date:
            await msg.answer(
                text="К сожалению, заказы по данной совместной закупке больше не принимаются",
                reply_markup=await make_keyboard(
                    [
                        f"{Config.MAKE_CUSTOM_PREFIX}{custom_type}"
                        for custom_type in await storage_client.get_custom_types_in_work()
                    ]
                ),
            )
        elif flag_user_in_working_custom:
            await msg.answer(
                text="К сожалению, Вы уже участвуете в данной закупке. При наличии вопросов свяжитесь с администратором",
                reply_markup=await make_keyboard(
                    [
                        f"{Config.MAKE_CUSTOM_PREFIX}{custom_type}"
                        for custom_type in await storage_client.get_custom_types_in_work()
                    ]
                ),
            )

    else:
        await msg.answer(
            text="В настоящий момент закупка с таким названием не производится",
            reply_markup=await make_keyboard(
                [
                    f"{Config.MAKE_CUSTOM_PREFIX}{custom_type}"
                    for custom_type in await storage_client.get_custom_types_in_work()
                ]
            ),
        )
