import asyncio
import datetime

import gspread
import pandas as pd
from gspread.exceptions import APIError

from bot.log import logger
from bot.texts import START_CUSTOM_MESSAGE
from config import Config


class CustomsClient:
    def __init__(self):
        self.client = gspread.service_account(filename=Config.GS_CONFIG).open(
            Config.GS_SHEET_NAME
        )

    async def _get_custom_df(self, custom_type: str) -> pd.DataFrame:
        loop = asyncio.get_running_loop()

        worksheet = await loop.run_in_executor(
            None,
            self.client.worksheet,
            f"{Config.CUSTOM_PRICE_WORKSHEET_PREFIX}_{custom_type}",
        )

        records = await loop.run_in_executor(None, worksheet.get_all_records)
        df = pd.DataFrame(records)

        return df

    async def get_all_custom_types(self):
        loop = asyncio.get_running_loop()

        worksheet_list = await loop.run_in_executor(None, self.client.worksheets)

        custom_types = [
            el.title.replace(f"{Config.CUSTOM_PRICE_WORKSHEET_PREFIX}_", "")
            for el in worksheet_list
            if el.title.startswith(Config.CUSTOM_PRICE_WORKSHEET_PREFIX)
        ]
        return custom_types

    async def make_custom_body(self, custom_type: str):
        custom_body = ""
        df = await self._get_custom_df(custom_type)
        for i in range(len(df)):
            if df.iloc[i, 0] == "-":
                custom_body += "\n"
                continue
            if df.iloc[i, 2] == "да":
                custom_body += f"{df.iloc[i, 0]} - {df.iloc[i, 1]} рублей\n"
        return custom_body

    async def make_start_custom_message(self, custom_type: str, expected_date: str):
        application_date = (
            datetime.datetime.now() + datetime.timedelta(days=2)
        ).replace(hour=10, minute=0, second=0, microsecond=0).strftime("%d-%m-%Y %H:%M")
        custom_body = await self.make_custom_body(custom_type)
        start_custom_message = START_CUSTOM_MESSAGE.format(
            custom_type=custom_type,
            expected_date=expected_date,
            application_date=application_date,
            custom_body=custom_body,
        )

        logger.info(f"Сообщение для закупки {custom_type} сформировано")
        return start_custom_message, application_date

    async def make_custom_worksheet(self, custom_type: str) -> str:
        loop = asyncio.get_running_loop()
        today = datetime.date.today().strftime("%d-%m-%Y")
        try:
            await loop.run_in_executor(
                None, self.client.add_worksheet, f"{custom_type}_{today}", 1, 1
            )
            logger.info(f"Создана новая страница для заказа {custom_type}")
        except APIError:
            today = False
        return today

    async def get_custom_df(self, custom_type: str):
        df = await self._get_custom_df(custom_type)
        df = df[df[Config.AVAILABLE_COLUMN_NAME] == "да"].dropna()
        return df

    async def insert_sync_df(
        self, insert_df: pd.DataFrame, custom_type: str, create_date: str
    ):
        loop = asyncio.get_running_loop()

        worksheet = await loop.run_in_executor(
            None, self.client.worksheet, f"{custom_type}_{create_date}"
        )

        await loop.run_in_executor(
            None,
            worksheet.update,
            [insert_df.columns.values.tolist()] + insert_df.values.tolist(),
        )
