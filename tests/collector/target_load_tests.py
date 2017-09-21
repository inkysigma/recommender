from recommender.collector.tools import create_batch
from . import ROOT_DIR
import unittest


class TargetLoadTest(unittest.TestCase):
    def test_create_batch(self):
        data = [(["hello", "hi"], "tmp/test.mp2")]
        track, target = create_batch(data, [
            "hello",
            "bonjour",
            "hi",
            "hola"
        ])
        print(target)


if __name__ == "__main__":
    unittest.main()
