import unittest
from src.delivery_service import calculate_delivery_cost as calc

ERROR = (-1, "0000-00-00")


class TestDeliveryValidation(unittest.TestCase):
    """Проверка входных данных: границы веса, дистанции, тип посылки."""

    def test_weight_below_minimum_returns_error(self):
        self.assertEqual(calc(0.05, 100, "обычный"), ERROR)

    def test_weight_above_maximum_returns_error(self):
        self.assertEqual(calc(50.1, 100, "обычный"), ERROR)

    def test_weight_minimum_boundary_is_valid(self):
        self.assertNotEqual(calc(0.1, 100, "обычный"), ERROR)

    def test_weight_maximum_boundary_is_valid(self):
        self.assertNotEqual(calc(50.0, 100, "обычный"), ERROR)

    def test_distance_zero_returns_error(self):
        self.assertEqual(calc(1, 0, "обычный"), ERROR)

    def test_distance_above_maximum_returns_error(self):
        self.assertEqual(calc(1, 5001, "обычный"), ERROR)

    def test_distance_boundaries_are_valid(self):
        self.assertNotEqual(calc(1, 1, "обычный"), ERROR)
        self.assertNotEqual(calc(1, 5000, "обычный"), ERROR)

    def test_unknown_package_type_returns_error(self):
        self.assertEqual(calc(1, 100, "срочный"), ERROR)


class TestDeliveryCost(unittest.TestCase):
    """Проверка расчёта стоимости (обычная доставка)."""

    def test_basic_cost_is_base_plus_distance(self):
        # 200 + 100 * 5 = 700
        self.assertEqual(calc(1, 100, "обычный")[0], 700)

    def test_weight_exactly_5_has_no_coefficient(self):
        self.assertEqual(calc(5.0, 100, "обычный")[0], 700)

    def test_weight_over_5_has_coefficient_1_2(self):
        self.assertEqual(calc(5.1, 100, "обычный")[0], 840)

    def test_weight_just_below_20_has_coefficient_1_2(self):
        self.assertEqual(calc(19.9, 100, "обычный")[0], 840)

    def test_weight_20_has_coefficient_1_5(self):
        self.assertEqual(calc(20.0, 100, "обычный")[0], 1050)

    def test_fragile_package_adds_300(self):
        self.assertEqual(calc(1, 100, "хрупкий")[0], 1000)

    def test_dangerous_package_adds_1000(self):
        self.assertEqual(calc(1, 100, "опасный")[0], 1700)

    def test_heavy_fragile_package_combines_coefficient_and_surcharge(self):
        # (700 * 1.2) + 300 = 1140
        self.assertEqual(calc(6, 100, "хрупкий")[0], 1140)

    def test_express_costs_more_than_regular(self):
        regular = calc(1, 100, "обычный")[0]
        express = calc(1, 100, "обычный", True)[0]
        self.assertGreater(express, regular)


class TestDeliveryDate(unittest.TestCase):
    """Проверка расчёта даты доставки (отправка 2026-09-03)."""

    def test_short_distance_takes_one_day(self):
        self.assertEqual(calc(1, 100, "обычный")[1], "2026-09-04")

    def test_distance_1000_takes_two_days(self):
        self.assertEqual(calc(1, 1000, "обычный")[1], "2026-09-05")

    def test_max_distance_takes_ten_days(self):
        self.assertEqual(calc(1, 5000, "обычный")[1], "2026-09-13")

    def test_express_long_distance_is_twice_as_fast(self):
        # 2000 км: обычная 4 дня, экспресс 2 дня
        self.assertEqual(calc(1, 2000, "обычный", True)[1], "2026-09-05")

    def test_express_short_distance_is_not_same_day(self):
        # минимальный срок доставки - 1 день, даже для экспресса
        self.assertNotEqual(calc(1, 100, "обычный", True)[1], "2026-09-03")

    def test_express_never_slower_than_regular(self):
        regular = calc(1, 1500, "обычный")[1]
        express = calc(1, 1500, "обычный", True)[1]
        self.assertLessEqual(express, regular)

    def test_result_is_tuple_of_int_and_str(self):
        result = calc(1, 100, "обычный")
        self.assertIsInstance(result, tuple)
        self.assertIsInstance(result[0], int)
        self.assertIsInstance(result[1], str)


if __name__ == "__main__":
    unittest.main()
