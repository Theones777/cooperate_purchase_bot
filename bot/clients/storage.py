from datetime import datetime

from tortoise import Tortoise, fields, run_async
from tortoise.models import Model

from bot.log import logger
from config import Config


class User(Model):
    id = fields.IntField(pk=True)
    tg_id = fields.IntField()
    full_name = fields.CharField(max_length=255)
    tg_user_name = fields.CharField(max_length=255)


class CustomsWork(Model):
    id = fields.IntField(pk=True)
    custom_type = fields.CharField(max_length=255)
    application_date = fields.CharField(max_length=255)
    create_date = fields.CharField(max_length=255)
    user_purchases = fields.JSONField(default=list)
    status_ready = fields.BooleanField()

    async def add_user_purchase(self, user_purchase: dict):
        self.user_purchases.append(user_purchase)
        await self.save()

    async def get_user_in_custom(self, user_id: dict):
        return any(str(user_id) in d for d in self.user_purchases)


class Storage:

    def __init__(self):
        run_async(self.init_db())

    @staticmethod
    async def init_db():
        await Tortoise.init(db_url=Config.DB_URL, modules={"models": ["bot.clients.storage"]})
        await Tortoise.generate_schemas()
        await Tortoise.get_connection("default").execute_script(
            "PRAGMA journal_mode=WAL;"
        )
        logger.info(f"База данных проинициализирована")

    @staticmethod
    async def save_new_user(user_id: int, user_full_name: str, tg_user_name: str):
        user, created = await User.get_or_create(
            tg_id=user_id,
            defaults={"full_name": user_full_name, "tg_user_name": tg_user_name},
        )
        if created:
            logger.info(f"Новый пользователь {user_full_name} добавлен")
        else:
            logger.info(f"Пользователь {user_full_name} уже существует")

    @staticmethod
    async def get_all_users_list() -> list:
        users = await User.all()
        return [user.tg_id for user in users]

    @staticmethod
    async def get_user_name(user_id: int) -> list:
        user = await User.filter(tg_id=str(user_id)).first()
        return user.full_name if user.full_name else user.tg_user_name

    @staticmethod
    async def save_custom_type_to_work(custom_type: str, application_date: str, create_date:str):
        if await CustomsWork.filter(custom_type=custom_type):
            await Storage.delete_custom_type_from_working(custom_type)
        await CustomsWork.create(
            custom_type=custom_type, application_date=application_date, create_date=create_date, status_ready=False
        )
        logger.info(f"Добавление заказа {custom_type} в работу")

    @staticmethod
    async def set_custom_ready(custom_type: str):
        custom = await CustomsWork.filter(custom_type=custom_type).first()
        custom.status_ready = True
        await custom.save()

    @staticmethod
    async def get_application_date(custom_type: str):
        custom = await CustomsWork.filter(custom_type=custom_type).first()
        application_date = custom.application_date
        return datetime.strptime(application_date, "%d-%m-%Y %H:%M")

    @staticmethod
    async def get_create_date(custom_type: str):
        custom = await CustomsWork.filter(custom_type=custom_type).first()
        return custom.create_date

    @staticmethod
    async def get_custom_types_in_work() -> list:
        custom_types = await CustomsWork.all()
        return [custom_type.custom_type for custom_type in custom_types if not custom_type.status_ready]

    @staticmethod
    async def check_user_in_working_custom(custom_type: str, user_id: int):
        custom_obj = await CustomsWork.get(custom_type=custom_type)
        return await custom_obj.get_user_in_custom(user_id)

    @staticmethod
    async def get_custom_users_list(custom_type: str) -> list:
        records = await Storage.get_customs_list(custom_type)
        return [list(record.keys())[0] for record in records]

    @staticmethod
    async def get_customs_list(custom_type: str) -> list:
        custom = await CustomsWork.filter(custom_type=custom_type).first()
        user_purchases = custom.user_purchases
        return user_purchases

    @staticmethod
    async def save_user_to_working_custom_type(custom_type: str, user_purchase: dict):
        custom_obj = await CustomsWork.get(custom_type=custom_type)
        await custom_obj.add_user_purchase(user_purchase)

        logger.info(
            f"Пользователь {list(user_purchase.keys())[0]} добавлен в закупку {custom_type}"
        )

    @staticmethod
    async def delete_custom_type_from_working(custom_type: str):
        await CustomsWork.filter(custom_type=custom_type).delete()

        logger.info(f"Закупка {custom_type} удалена из базы данных")
