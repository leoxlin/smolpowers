import unittest

from greeting import greet


class GreetingTest(unittest.TestCase):
    def test_greeting(self) -> None:
        self.assertEqual(greet(), "hello from smolpowers")


if __name__ == "__main__":
    unittest.main()
