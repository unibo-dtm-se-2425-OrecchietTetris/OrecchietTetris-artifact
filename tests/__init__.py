import unittest
from OrecchietTetris import MyClass


class TestMyClass(unittest.TestCase):
    # test methods' names should begin with `test_`
    def test_my_method(self) -> None:
        x = MyClass().my_method()
        self.assertEqual("Hello World", x)
