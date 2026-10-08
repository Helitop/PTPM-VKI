import logging
import unittest

from src.my_project import validate_registration, mask_password

# Убираем вывод логов в консоль на время тестов (запись в файл остаётся)
for _h in list(logging.getLogger().handlers):
    if type(_h) is logging.StreamHandler:
        logging.getLogger().removeHandler(_h)

GOOD_PWD = "Пароль123!"


class TestSuccessfulRegistration(unittest.TestCase):
    """Корректные данные: все три вида логина."""

    def test_valid_string_login_returns_true(self):
        self.assertEqual(validate_registration("ivan_99", GOOD_PWD, GOOD_PWD), ("True", ""))

    def test_valid_phone_login_returns_true(self):
        self.assertEqual(validate_registration("+7-999-123-4567", GOOD_PWD, GOOD_PWD), ("True", ""))

    def test_valid_email_login_returns_true(self):
        self.assertEqual(validate_registration("user@test.ru", GOOD_PWD, GOOD_PWD), ("True", ""))

    def test_login_with_exactly_5_chars_is_valid(self):
        self.assertEqual(validate_registration("ab_12", GOOD_PWD, GOOD_PWD)[0], "True")

    def test_password_with_exactly_7_chars_is_valid(self):
        self.assertEqual(validate_registration("ivan_99", "Парол1!", "Парол1!")[0], "True")


class TestLoginValidation(unittest.TestCase):
    """Проверка логина: строка, чёрный список, телефон, email."""

    def test_string_login_shorter_than_5_returns_false(self):
        result, msg = validate_registration("usr1", GOOD_PWD, GOOD_PWD)
        self.assertEqual(result, "False")
        self.assertIn("5 символов", msg)

    def test_string_login_with_cyrillic_returns_false(self):
        self.assertEqual(validate_registration("иван_99", GOOD_PWD, GOOD_PWD)[0], "False")

    def test_string_login_with_hyphen_returns_false(self):
        self.assertEqual(validate_registration("ivan-99", GOOD_PWD, GOOD_PWD)[0], "False")

    def test_blacklisted_login_returns_false(self):
        result, msg = validate_registration("admin", GOOD_PWD, GOOD_PWD)
        self.assertEqual(result, "False")
        self.assertIn("запрещенных", msg)

    def test_blacklisted_login_in_uppercase_returns_false(self):
        self.assertEqual(validate_registration("ADMIN", GOOD_PWD, GOOD_PWD)[0], "False")

    def test_phone_without_dashes_returns_false(self):
        self.assertEqual(validate_registration("+79991234567", GOOD_PWD, GOOD_PWD)[0], "False")

    def test_phone_with_letters_returns_false(self):
        self.assertEqual(validate_registration("+7-abc-123-4567", GOOD_PWD, GOOD_PWD)[0], "False")

    def test_email_without_domain_dot_returns_false(self):
        self.assertEqual(validate_registration("user@test", GOOD_PWD, GOOD_PWD)[0], "False")

    def test_email_with_double_at_returns_false(self):
        self.assertEqual(validate_registration("user@@test.ru", GOOD_PWD, GOOD_PWD)[0], "False")

    def test_email_with_consecutive_dots_in_domain_returns_false(self):
        self.assertEqual(validate_registration("user@test..ru", GOOD_PWD, GOOD_PWD)[0], "False")

    def test_email_with_trailing_dot_returns_false(self):
        self.assertEqual(validate_registration("user@test.ru.", GOOD_PWD, GOOD_PWD)[0], "False")

    def test_email_domain_label_ending_with_hyphen_returns_false(self):
        self.assertEqual(validate_registration("user@test-.ru", GOOD_PWD, GOOD_PWD)[0], "False")


class TestPasswordValidation(unittest.TestCase):
    """Проверка пароля: длина, символы, регистр, цифра, спецсимвол, совпадение."""

    def test_different_confirmation_returns_false(self):
        result, msg = validate_registration("ivan_99", "Пароль123!", "Пароль123?")
        self.assertEqual(result, "False")
        self.assertIn("не совпадают", msg)

    def test_password_shorter_than_7_returns_false(self):
        result, msg = validate_registration("ivan_99", "Па1!", "Па1!")
        self.assertEqual(result, "False")
        self.assertIn("7 символов", msg)

    def test_empty_password_returns_false(self):
        self.assertEqual(validate_registration("ivan_99", "", "")[0], "False")

    def test_password_with_latin_returns_false(self):
        self.assertEqual(validate_registration("ivan_99", "Password123!", "Password123!")[0], "False")

    def test_password_without_uppercase_returns_false(self):
        result, msg = validate_registration("ivan_99", "пароль123!", "пароль123!")
        self.assertEqual(result, "False")
        self.assertIn("заглавную", msg)

    def test_password_without_lowercase_returns_false(self):
        result, msg = validate_registration("ivan_99", "ПАРОЛЬ123!", "ПАРОЛЬ123!")
        self.assertEqual(result, "False")
        self.assertIn("строчную", msg)

    def test_password_without_digit_returns_false(self):
        result, msg = validate_registration("ivan_99", "Пароль!!!", "Пароль!!!")
        self.assertEqual(result, "False")
        self.assertIn("цифру", msg)

    def test_password_without_special_char_returns_false(self):
        result, msg = validate_registration("ivan_99", "Пароль1234", "Пароль1234")
        self.assertEqual(result, "False")
        self.assertIn("специальный", msg)


class TestPasswordMasking(unittest.TestCase):
    """Маскирование паролей и отсутствие паролей в логах."""

    def test_same_passwords_give_same_mask(self):
        self.assertEqual(mask_password("Пароль123!"), mask_password("Пароль123!"))

    def test_different_passwords_give_different_masks(self):
        self.assertNotEqual(mask_password("Пароль123!"), mask_password("Пароль123?"))

    def test_empty_password_mask_is_marker(self):
        self.assertEqual(mask_password(""), "[EMPTY]")

    def test_mask_does_not_contain_plain_password(self):
        self.assertNotIn("Пароль123!", mask_password("Пароль123!"))

    def test_logs_of_successful_registration_do_not_contain_password(self):
        with self.assertLogs(level="DEBUG") as cm:
            validate_registration("ivan_99", GOOD_PWD, GOOD_PWD)
        self.assertNotIn(GOOD_PWD, "\n".join(cm.output))

    def test_logs_of_failed_registration_do_not_contain_password(self):
        with self.assertLogs(level="DEBUG") as cm:
            validate_registration("admin", GOOD_PWD, GOOD_PWD)
        self.assertNotIn(GOOD_PWD, "\n".join(cm.output))


if __name__ == "__main__":
    unittest.main()
