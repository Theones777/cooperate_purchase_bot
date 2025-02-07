from os import getenv

from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = getenv("BOT_TOKEN")
    ADMIN_IDS = getenv("ADMIN_IDS")
    GS_CONFIG = getenv("GS_CONFIG")
    GS_SHEET_NAME = getenv("GS_SHEET_NAME")

    DB_URL = getenv("DB_URL", "sqlite://data/database.db")
    CUSTOM_PRICE_WORKSHEET_PREFIX = getenv("CUSTOM_PRICE_WORKSHEET_PREFIX", "прайс")
    MAKE_CUSTOM_PREFIX = getenv("MAKE_CUSTOM_PREFIX", "Сделать заказ ")
    PRODUCT_NAME_COLUMN_NAME = getenv("PRODUCT_NAME_COLUMN_NAME", "Товар")
    PRODUCT_PRICE_COLUMN_NAME = getenv("PRODUCT_PRICE_COLUMN_NAME", "Цена")
    AVAILABLE_COLUMN_NAME = getenv("AVAILABLE_COLUMN_NAME", "Есть в закупке")
