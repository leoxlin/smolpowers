import subprocess
import unittest


class GreetTest(unittest.TestCase):
    def test_greeting(self) -> None:
        result = subprocess.run(
            ["bin/greet.sh"],
            capture_output=True,
            check=True,
            text=True,
        )
        self.assertEqual(result.stdout, "hello from mixed skills\n")


if __name__ == "__main__":
    unittest.main()
