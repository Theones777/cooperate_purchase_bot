import traceback
from datetime import datetime
from enum import Enum

import pandas as pd
from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeDefault,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from thefuzz import process

from bot.clients.init_clients import storage_client, gs_client
from bot.log import logger
from config import Config


class MailingTypes(Enum):
    massive = "Общая"
    specified = "Заказавшим"


class AdminConfirmButtons(Enum):
    sure = "Уверен"


class UserConfirmButtons(Enum):
    sure = "Уверен"
    cancel = "Отмена"


class UserPaymentButton(Enum):
    payed = "Оплачено"
    error = "Ошибка оплаты"
    cancel = "Отменить заказ"


async def get_admin_ids() -> list:
    return set([int(el.strip()) for el in Config.ADMIN_IDS.split(",")])


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Начать использование бота"),
        BotCommand(command="help", description="Помощь"),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def make_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


async def mailing(
    bot: Bot,
    mailing_type: str,
    custom_type: str,
    mailing_message: str,
    buttons: list = None,
):
    if mailing_type == MailingTypes.massive.value:
        mailing_list = await storage_client.get_all_users_list()
    else:
        mailing_list = await storage_client.get_custom_users_list(custom_type)
    for user_id in mailing_list:
        try:
            if buttons:
                await bot.send_message(
                    chat_id=user_id,
                    text=mailing_message,
                    reply_markup=await make_keyboard(buttons),
                )
            else:
                await bot.send_message(
                    chat_id=user_id,
                    text=mailing_message,
                    reply_markup=ReplyKeyboardRemove(),
                )
        except:
            pass


async def check_user_custom_format(user_custom: str, custom_type: str) -> str:
    refactored_user_custom = ""
    custom_cost = 0
    custom_df = await gs_client.get_custom_df(custom_type)
    products_list = custom_df[Config.PRODUCT_NAME_COLUMN_NAME].tolist()
    try:
        for string in user_custom.split("\n"):
            if string:
                string_split = string.split("-")
                product = process.extractOne(string_split[0].strip(), products_list)[0]
                product_count = int(string_split[1].strip())
                product_price = custom_df[
                    custom_df[Config.PRODUCT_NAME_COLUMN_NAME] == product
                ][Config.PRODUCT_PRICE_COLUMN_NAME].values[0]
                custom_cost += product_price * product_count
                refactored_user_custom += f"{product} - {product_count}\n"
    except Exception as e:
        logger.warning(f"Ошибка введенного формата\n {e}")
        return False

    return refactored_user_custom, custom_cost


async def check_custom_application_date(custom_type: str) -> bool:
    now = datetime.now()
    application_date = await storage_client.get_application_date(custom_type)
    if now > application_date:
        return False
    return True


async def sync_db_to_gs(custom_type: str) -> bool:
    async def refactor_user_purchase(user_purchase_dict: dict, qr: str, pay_status: int, df: pd.DataFrame) -> list:
        products = df[Config.PRODUCT_NAME_COLUMN_NAME].tolist()
        product_price = df[Config.PRODUCT_PRICE_COLUMN_NAME].tolist()
        result = []
        summ_value = 0

        for i, product in enumerate(products):
            if product in user_purchase_dict:
                product_count = user_purchase_dict[product]
                summ_value += product_count * int(product_price[i])
            else:
                product_count = 0
            result.append(product_count)
        result.append(summ_value)
        result.append(qr)
        result.append(pay_status)
        return result

    async def str_to_dict(user_input: str):
        result = {}
        for string in user_input.split("\n"):
            if string:
                string_split = string.split("-")
                product, product_count = string_split[0].strip(), string_split[1].strip()
                result[product] = int(product_count)

        return result

    df_dict = {}
    gs_df = await gs_client.get_custom_df(custom_type)
    df_dict[Config.PRODUCT_NAME_COLUMN_NAME] = gs_df[Config.PRODUCT_NAME_COLUMN_NAME].tolist()
    df_dict[Config.PRODUCT_NAME_COLUMN_NAME].append("Итого")
    df_dict[Config.PRODUCT_NAME_COLUMN_NAME].append("QR-code")
    df_dict[Config.PRODUCT_NAME_COLUMN_NAME].append("Оплачено")
    try:
        customs_list = await storage_client.get_customs_list(custom_type)
        for user_purchase_info in customs_list:
            user_name = await storage_client.get_user_name(user_purchase_info[0])
            user_purchase = await str_to_dict(user_purchase_info[1])
            qr_code = user_purchase_info[2]
            payed_status = user_purchase_info[3]
            df_dict[user_name] = await refactor_user_purchase(user_purchase, qr_code, payed_status, gs_df)

        create_date = await storage_client.get_create_date(custom_type)
        await gs_client.insert_sync_df(pd.DataFrame(df_dict), custom_type, create_date)
    except Exception as e:
        logger.error(f"Ошибка синхронизации {e}")
        traceback.print_exc()
        return False
    return True
