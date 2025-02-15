from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from bot.clients.init_clients import storage_client, pyro_client
from bot.states import User
from bot.texts import (
    CUSTOM_CONFIRM_MESSAGE,
    CUSTOM_TEMPLATE,
    PAYMENT_MESSAGE,
    CUSTOM_DONE_MESSAGE,
    CUSTOM_NOT_ACCEPTED_MESSAGE,
)
from bot.utils import (
    make_keyboard,
    make_inline_keyboard,
    UserConfirmButtons,
    check_user_custom_format,
    check_custom_application_date,
    UserPaymentButton,
    price_str_to_template_body,
)
from config import Config

user_router = Router()

@user_router.callback_query(User.payed, F.data.in_([el.name for el in UserPaymentButton]))
async def payed(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    custom_type = user_data.get("custom_type")
    if callback.data == UserPaymentButton.payed.name:
        payment_link = user_data.get("payment_link")

        if await pyro_client.check_user_payment():
            payment_accepted = True
            callback_message = "Спасибо за Ваш заказ!"
            message = CUSTOM_DONE_MESSAGE
            await callback.answer(
                text=callback_message,
                show_alert=False
            )
        else:
            payment_accepted = False
            callback_message = CUSTOM_NOT_ACCEPTED_MESSAGE
            message = "Спасибо за Ваш заказ!"
            await callback.answer(
                text=callback_message,
                show_alert=True
            )

        await storage_client.update_user_custom_payed(
            custom_type, payment_link, callback.from_user.id, payment_accepted
        )

        keyboard = await make_keyboard(
            [
                f"{Config.MAKE_CUSTOM_PREFIX}{custom_type}"
                for custom_type in await storage_client.get_custom_types_in_work()
            ]
        )
        await state.clear()


    elif callback.data == UserPaymentButton.error.name:
        custom_cost = user_data.get("custom_cost")
        payment_link = await pyro_client.get_payment_link(custom_cost)
        if "Ошибка" not in payment_link:
            await state.update_data(payment_link=payment_link[0])

            message = PAYMENT_MESSAGE.format(
                custom_cost=custom_cost,
                payment_link=payment_link[1],
            )
            keyboard = await make_inline_keyboard(UserPaymentButton)
            await state.set_state(User.payed)
        else:
            keyboard = ReplyKeyboardRemove()
            message = payment_link
            await state.clear()

    elif callback.data == UserPaymentButton.cancel.name:
        await storage_client.delete_user_custom(custom_type, callback.from_user.id)
        message = f"Закупка {custom_type} отменена"
        keyboard = await make_keyboard(
            [
                f"{Config.MAKE_CUSTOM_PREFIX}{custom_type}"
                for custom_type in await storage_client.get_custom_types_in_work()
            ]
        )
        await state.clear()
    else:
        message = "Я Вас не понял, пожалуйста, нажмите кнопку"
        keyboard = await make_keyboard([el.value for el in UserPaymentButton])

    await callback.message.answer(
        text=message,
        reply_markup=keyboard
    )

    await callback.answer()


@user_router.message(User.confirm, F.text.in_([el.value for el in UserConfirmButtons]))
async def confirm(msg: Message, state: FSMContext):
    if msg.text == UserConfirmButtons.sure.value:
        user_data = await state.get_data()
        custom_type = user_data.get("custom_type")
        user_custom = user_data.get("user_custom")
        custom_cost = user_data.get("custom_cost")
        user_purchase = {msg.from_user.id: user_custom}
        await storage_client.save_user_to_working_custom_type(custom_type, user_purchase, custom_cost)
        await msg.answer(
            text=CUSTOM_CONFIRM_MESSAGE,
            reply_markup=ReplyKeyboardRemove()
        )
        payment_link = await pyro_client.get_payment_link(custom_cost)
        if "Ошибка" not in payment_link:
            await state.update_data(payment_link=payment_link[0])
            keyboard = await make_inline_keyboard(UserPaymentButton)
            message = PAYMENT_MESSAGE.format(
                custom_cost=custom_cost,
                payment_link=payment_link[1]
            )
            await state.set_state(User.payed)
        else:
            keyboard=ReplyKeyboardRemove()
            message = payment_link
            await state.clear()
    else:
        message = "Заказ отменен"
        keyboard = await make_keyboard(
            [
                f"{Config.MAKE_CUSTOM_PREFIX}{custom_type}"
                for custom_type in await storage_client.get_custom_types_in_work()
            ]
        )
        await state.clear()

    await msg.answer(
        text=message,
        reply_markup=keyboard,
    )


@user_router.message(User.user_custom)
async def custom_inserted(msg: Message, state: FSMContext):
    user_custom = msg.text.lower()
    user_data = await state.get_data()
    custom_type = user_data.get("custom_type")
    if user_custom := await check_user_custom_format(user_custom, custom_type):
        await state.update_data(user_custom=user_custom[0])
        await state.update_data(custom_cost=user_custom[1])
        await msg.answer(
            text=f"Вы уверены, что хотите сделать заказ?\n"
                 f"Закупка - <b>{custom_type}</b>\n"
                 f"Состав: \n{user_custom[0]}\n"
                 f"Итоговая стоимость: {user_custom[1]}",
            reply_markup=await make_keyboard([el.value for el in UserConfirmButtons])
        )
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
            template_body = await price_str_to_template_body(await storage_client.get_price_str(custom_type))
            message = CUSTOM_TEMPLATE.format(
                template_body = template_body
            )
            keyboard = ReplyKeyboardRemove()
            await state.set_state(User.user_custom)
        elif not flag_application_date:
            message = "К сожалению, заказы по данной совместной закупке больше не принимаются"
            keyboard = await make_keyboard(
                [
                    f"{Config.MAKE_CUSTOM_PREFIX}{custom_type}"
                    for custom_type in await storage_client.get_custom_types_in_work()
                ]
            )
        elif flag_user_in_working_custom:
            message = "Вы уже участвуете в данной закупке. При наличии вопросов свяжитесь с администратором"
            keyboard = await make_keyboard(
                [
                    f"{Config.MAKE_CUSTOM_PREFIX}{custom_type}"
                    for custom_type in await storage_client.get_custom_types_in_work()
                ]
            )
        else:
            message = "Ошибка"
            keyboard = ReplyKeyboardRemove()

    else:
        message = "В настоящий момент закупка с таким названием не производится"
        keyboard = await make_keyboard(
            [
                f"{Config.MAKE_CUSTOM_PREFIX}{custom_type}"
                for custom_type in await storage_client.get_custom_types_in_work()
            ]
        )
    await msg.answer(text=message, reply_markup=keyboard)
