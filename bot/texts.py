START_ADMIN_MESSAGE = (
    "Привет! У Вас есть права администратора!\n"
    "Команды, доступные администратору:\n"
    "/start_custom - Начать закупку,\n"
    "/delay_custom - Задержка заказа,\n"
    "/payment_received - Оплата получена,\n"
    "/ready_custom - Заказ готов к выдаче,\n"
    "/message_mailing - Рассылка,\n"
    "/sync - Синхронизировать данные в базе данных с Гугл-таблицей,\n"
    "/cancel - возврат к началу"
)

START_USER_MESSAGE = (
    "Привет! Я бот для проведения совместной закупки из <b>Bhajan Cafe</b>. "
    "При проведении новой закупки я отправлю Вам сообщение"
)

HELP_MESSAGE = "Номер для связи - +7 123 456789 Шурик"

READY_MESSAGE = "Добрый день) Заказ по закупке {custom_type} готов к выдаче"

DELAY_MESSAGE = (
    "Добрый день! Приносим свои извинения, поставка <u>{custom_type}</u> задерживается.\n"
    "Ожидаем <b>{expected_date}</b>"
)

START_CUSTOM_MESSAGE = (
    "\nПриветствую, дорогие гости и друзья!\n\n"
    "Стартует закупка <b>{custom_type}</b>\n"
    "Ожидаемая дата поставки <b>{expected_date}</b>\n"
    "Заказы принимаем до <b> {application_date}</b>\n\n"
    "{custom_body}\n\n"
    "особое ВНИМАНИЕ пунктам внизу\n"
    "   без оплатное хранение товара 1 сутки, далее 30 руб/сутки до 3-х дней. "
    "Затем заказ расформировывается и совместная закупка более будет недоступна.\n"
    "   оплата наличными или по qr-коду. На заказы от 3000 скидка 3%. На заказы менее 500руб - наценка 10%.\n"
    "   помните, что бы забрать продукцию - вам потребуется сумка. "
    "Мы используем только фасовочные пластиковые пакеты! Пакеты маечки мы не используем!\n"
    "   заказ компании {custom_type} - это продукция, которая требует специальных условий транспортировки, "
    "поэтому собирая совместный заказ мы его планируем, но не факт, что сможем выполнить в полном объеме, "
    "о чем вас заранее предупредим\n"
)

CUSTOM_CONFIRM_MESSAGE = "Заказ принят, ожидайте сообщение об оплате"

CUSTOM_TEMPLATE = (
    "Введите, пожалуйста Ваш заказ в формате:\n"
    "<i>Товар1 - количество\n"
    "Товар2 - количество ... </i>\n"
)

PAYMENT_MESSAGE = (
    "Сумма Вашего заказа = <b>{custom_cost}</b> рублей\n"
    "После оплаты, пожалуйста, нажмите кнопку внизу\n"
    "Ссылка на оплату:\n\n"
    "{payment_link}"
)

CUSTOM_DONE_MESSAGE = "Благодарим за оплату! Когда заказ будет готов к выдаче, Вам придет от меня сообщение!"

PAYMENT_RECEIVED_MESSAGE = "Оплата по заказу {custom_type} получена. Благодарим за заказ, оповестим по готовности"

MAILING_CONFIRM_TEMPLATE = (
    "Вы уверены, что хотите отправить данное сообщение?\n"
    "Тип рассылки - {mailing_type}\n"
    "Закупка - {custom_type}\n"
    "Сообщение:\n"
    "{mailing_message}"
)
