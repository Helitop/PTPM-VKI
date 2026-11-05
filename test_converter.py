import unittest
from converter import Converter


class TestConverter(unittest.TestCase):

    # --- Диапазон 1: [100.7; +∞) -> 1000 ---
    def test_upper_bound_exact(self):
        """[100.7; +∞): Ровно нижняя граница 100.7"""
        self.assertEqual(Converter.do(100.7), 1000)

    def test_upper_bound_near(self):
        """[100.7; +∞): Чуть выше границы (100.8)"""
        self.assertEqual(Converter.do(100.8), 1000)

    def test_upper_bound_large(self):
        """[100.7; +∞): Заведомо большое число (500.0)"""
        self.assertEqual(Converter.do(500.0), 1000)

    # --- Диапазон 2: (0; 100.7) -> int(x) ---
    def test_positive_range_below_bound(self):
        """(0; 100.7): Впритирку к верхней границе (100.6)"""
        self.assertEqual(Converter.do(100.6), 100)

    def test_positive_range_typical(self):
        """(0; 100.7): Типичное значение из условия (65.7)"""
        self.assertEqual(Converter.do(65.7), 65)

    def test_positive_range_near_zero(self):
        """(0; 100.7): Минимальное положительное число (0.1)"""
        self.assertEqual(Converter.do(0.1), 0)

    # --- Точка 3: x == 0.0 -> ValueError ---
    def test_zero_raises_value_error(self):
        """x == 0.0: Проверка выброса ValueError"""
        with self.assertRaises(ValueError):
            Converter.do(0.0)

    def test_zero_negative_float_raises_value_error(self):
        """x == -0.0: Проверка на отрицательный ноль во float"""
        with self.assertRaises(ValueError):
            Converter.do(-0.0)

    # --- Диапазон 4: [-30.4; 0) -> int(x) - 5 ---
    def test_negative_middle_near_zero(self):
        """[-30.4; 0): Впритирку к нулю с минуса (-0.1)"""
        self.assertEqual(Converter.do(-0.1), -5)

    def test_negative_middle_typical(self):
        """[-30.4; 0): Типичное значение в середине (-10.5)"""
        self.assertEqual(Converter.do(-10.5), -15)

    def test_negative_middle_lower_bound(self):
        """[-30.4; 0): Ровно нижняя граница (-30.4)"""
        self.assertEqual(Converter.do(-30.4), -35)

    # --- Диапазон 5: (-∞; -30.5] -> -2000 ---
    def test_lower_bound_exact(self):
        """(-∞; -30.5]: Ровно верхняя граница (-30.5)"""
        self.assertEqual(Converter.do(-30.5), -2000)

    def test_lower_bound_below(self):
        """(-∞; -30.5]: Чуть ниже границы (-30.6)"""
        self.assertEqual(Converter.do(-30.6), -2000)

    def test_lower_bound_large_negative(self):
        """(-∞; -30.5]: Заведомо малое число из условия (-94.5)"""
        self.assertEqual(Converter.do(-94.5), -2000)



if __name__ == '__main__':
    unittest.main(verbosity=2)