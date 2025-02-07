# Бот для проведения совместной закупки

## Для запуска бота необходимо:
1. Создать .env файл в корне проекта. Указать переменные:
- BOT_TOKEN = токен бота от BotFather
- ADMIN_IDS = id пользователей ТГ, у которых должны быть права админа
- GS_CONFIG = имя json-файла с кредами для подключения к Google API
- GS_SHEET_NAME = название Google-таблицы со сводными данными

При необходимости:
- DB_URL = токен бота от BotFather
- CUSTOM_PRICE_WORKSHEET_PREFIX = id пользователей ТГ, у которых должны быть права админа
- MAKE_CUSTOM_PREFIX = имя json-файла с кредами для подключения к Google API
- PRODUCT_NAME_COLUMN_NAME = название Google-таблицы со сводными данными
- PRODUCT_PRICE_COLUMN_NAME = название Google-таблицы со сводными данными
- AVAILABLE_COLUMN_NAME = название Google-таблицы со сводными данными

2. Получить json-файл с кредами для подключения к Google API. И положить его в корень проекта


## N.B! Нельзя подключаться к БД во время работы бота через docker. 
Для внесения изменений в БД:
1. Остановить работу бота;
2. Скопировать все 3 файла БД в другое место;
3. Подключиться к новой БД;
4. Внести изменения и сохранить их;
5. Перенести 3 новых файла в том БД бота;
6. Запустить контейнер с ботом
