import hashlib
import logging
import os
import re
import sys

# 1. Автоматическое создание папки logs согласно требованиям
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 2. Настройка логирования (в консоль и файл)
log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    datefmt=date_format,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(LOG_DIR, "file_txt.log"), encoding="utf-8"
        ),
    ],
)

# Черный список логинов
BLACKLIST = {
    "admin",
    "administrator",
    "root",
    "superuser",
    "moderator",
    "support",
    "guest",
    "test",
    "null",
    "undefined",
}

# Регулярные выражения для валидации
PHONE_PATTERN = re.compile(r"^\+\d-\d{3}-\d{3}-\d{4}$")
EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9_+-]+(\.[a-zA-Z0-9_+-]+)*"
    r"@[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?"
    r"(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)+$"
)
STRING_LOGIN_ALLOWED = re.compile(r"^[a-zA-Z0-9_]+$")

# Кириллица (включая Ёё), цифры и спецсимволы
CYRILLIC_LOWER = re.compile(r"[а-яё]")
CYRILLIC_UPPER = re.compile(r"[А-ЯЁ]")
DIGIT = re.compile(r"\d")
# Набор стандартных спецсимволов
SPECIAL_CHARS = r"""!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~ """
PASSWORD_VALID_CHARS = re.compile(rf"^[а-яёА-ЯЁ0-9{re.escape(SPECIAL_CHARS)}]+$")
SPECIAL_CHAR_CHECK = re.compile(rf"[{re.escape(SPECIAL_CHARS)}]")


def mask_password(password: str) -> str:
    """
    Маскирует пароль с помощью хеша sha256.
    Одинаковые пароли дают одинаковую маску, разные — разную.
    Пароль в открытом виде в логи не попадает.
    """
    if not password:
        return "[EMPTY]"
    hashed = hashlib.sha256(password.encode("utf-8")).hexdigest()[:8]
    return f"***MASKED_{hashed}***"


def validate_registration(
    login: str, password: str, confirm_password: str
) -> tuple[str, str]:
    """
    Валидация учетных данных пользователя.
    Возвращает:
      - Строка1 (Результат): "True" или "False"
      - Строка2 (Сообщение): "" при успехе или текст ошибки (12 вариантов ошибок).
    """
    masked_pwd = mask_password(password)
    masked_conf = mask_password(confirm_password)

    logging.debug(
        f"Начало валидации для login='{login}', password={masked_pwd}, confirm={masked_conf}"
    )

    # 1. Проверка совпадения паролей
    if password != confirm_password:
        msg = "Пароль и подтверждение пароля не совпадают"
        logging.warning(
            f"Отказ регистрации [login='{login}', pwd={masked_pwd}, conf={masked_conf}]: {msg}"
        )
        return "False", msg

    # 2. Проверка черного списка логинов
    if login.strip().lower() in BLACKLIST:
        msg = "Логин находится в списке запрещенных имен"
        logging.warning(
            f"Отказ регистрации [login='{login}', pwd={masked_pwd}]: {msg}"
        )
        return "False", msg

    # 3. Валидация логина (телефон / email / строка)
    if login.startswith("+"):
        # Попытка проверки как телефон
        if not PHONE_PATTERN.fullmatch(login):
            msg = "Неверный формат номера телефона (ожидается формат +x-xxx-xxx-xxxx)"
            logging.warning(
                f"Отказ регистрации [login='{login}', pwd={masked_pwd}]: {msg}"
            )
            return "False", msg
    elif "@" in login:
        # Попытка проверки как email
        if not EMAIL_PATTERN.fullmatch(login):
            msg = "Неверный формат адреса электронной почты"
            logging.warning(
                f"Отказ регистрации [login='{login}', pwd={masked_pwd}]: {msg}"
            )
            return "False", msg
    else:
        # Обычный строковый логин
        if len(login) < 5:
            msg = "Длина логина должна быть не менее 5 символов"
            logging.warning(
                f"Отказ регистрации [login='{login}', pwd={masked_pwd}]: {msg}"
            )
            return "False", msg

        if not STRING_LOGIN_ALLOWED.fullmatch(login):
            msg = "Логин может содержать только латинские буквы, цифры и символ подчеркивания '_'"
            logging.warning(
                f"Отказ регистрации [login='{login}', pwd={masked_pwd}]: {msg}"
            )
            return "False", msg

    # 4. Валидация пароля
    if len(password) < 7:
        msg = "Длина пароля должна быть не менее 7 символов"
        logging.warning(
            f"Отказ регистрации [login='{login}', pwd={masked_pwd}]: {msg}"
        )
        return "False", msg

    if not PASSWORD_VALID_CHARS.fullmatch(password):
        msg = "Пароль должен содержать только кириллицу, цифры и спецсимволы (латиница запрещена)"
        logging.warning(
            f"Отказ регистрации [login='{login}', pwd={masked_pwd}]: {msg}"
        )
        return "False", msg

    if not CYRILLIC_UPPER.search(password):
        msg = "Пароль должен содержать как минимум одну заглавную букву (кириллица)"
        logging.warning(
            f"Отказ регистрации [login='{login}', pwd={masked_pwd}]: {msg}"
        )
        return "False", msg

    if not CYRILLIC_LOWER.search(password):
        msg = "Пароль должен содержать как минимум одну строчную букву (кириллица)"
        logging.warning(
            f"Отказ регистрации [login='{login}', pwd={masked_pwd}]: {msg}"
        )
        return "False", msg

    if not DIGIT.search(password):
        msg = "Пароль должен содержать как минимум одну цифру"
        logging.warning(
            f"Отказ регистрации [login='{login}', pwd={masked_pwd}]: {msg}"
        )
        return "False", msg

    if not SPECIAL_CHAR_CHECK.search(password):
        msg = "Пароль должен содержать как минимум один специальный символ"
        logging.warning(
            f"Отказ регистрации [login='{login}', pwd={masked_pwd}]: {msg}"
        )
        return "False", msg

    # Успех
    logging.info(
        f"Успешная регистрация пользователя: login='{login}', pwd={masked_pwd}, conf={masked_conf}"
    )
    return "True", ""


# Демонстрация работы
if __name__ == "__main__":
    logging.info("=== Запуск демонстрационных сценариев ===")

    # Примеры тестовых наборов (включая позитивные и негативные сценарии)
    test_cases = [
        # Успешный строковый логин (пароль: кириллица верх/низ + цифра + спецсимвол)
        ("ivan_99", "Пароль123!", "Пароль123!"),
        # Успешный телефон
        ("+7-999-123-4567", "Секрет1#", "Секрет1#"),
        # Успешный email
        ("user@test.ru", "Привет456%", "Привет456%"),
        # Ошибка 1: Пароли не совпадают
        ("ivan_99", "Пароль123!", "Пароль123?"),
        # Ошибка 2: Черный список
        ("admin", "Пароль123!", "Пароль123!"),
        # Ошибка 3: Телефон не по маске
        ("+79991234567", "Пароль123!", "Пароль123!"),
        # Ошибка 4: Некорректный email
        ("user@@test..ru", "Пароль123!", "Пароль123!"),
        # Ошибка 5: Короткий строковый логин
        ("usr", "Пароль123!", "Пароль123!"),
        # Ошибка 6: Запрещенные символы в логине (кириллица)
        ("иван_99", "Пароль123!", "Пароль123!"),
        # Ошибка 7: Короткий пароль (< 7)
        ("valid_login", "Па1!", "Па1!"),
        # Ошибка 8: Латиница в пароле
        ("valid_login", "Password123!", "Password123!"),
        # Ошибка 9: Нет заглавной кириллицы
        ("valid_login", "пароль123!", "пароль123!"),
        # Ошибка 10: Нет строчной кириллицы
        ("valid_login", "ПАРОЛЬ123!", "ПАРОЛЬ123!"),
        # Ошибка 11: Нет цифры
        ("valid_login", "Пароль!!!", "Пароль!!!"),
        # Ошибка 12: Нет спецсимвола
        ("valid_login", "Пароль1234", "Пароль1234"),
    ]

    print("\n" + "=" * 50)
    for idx, (l, p, cp) in enumerate(test_cases, 1):
        try:
            res, msg = validate_registration(l, p, cp)
            print(f"Тест #{idx:02d}: Результат = {res} | Сообщение = '{msg}'")
        except Exception as e:
            # Демонстрация логирования непредвиденных сбоев с traceback
            logging.exception(f"Критический сбой при обработке: {e}")

    print("=" * 50)
    logging.info("=== Завершение демонстрационных сценариев ===")