from recommender.collector.saver import FileSaver
import logging
import unittest
import numpy as np


class FileSaverTests(unittest.TestCase):
    def setUp(self):
        self.saver = FileSaver("tmp/file.save", logging.getLogger("file_saver"))

    def test_append(self):
        self.saver.append_results(["hello"], np.zeros(shape=(1, 100)))
        self.saver.append_results(["hi"], np.ones(shape=(1, 100)))
        self.saver.append_results(["hi"], np.zeros(shape=(1, 100)))

    def test_condense(self):
        self.saver.condense_file()

    def test_save(self):
        self.saver.save_results(["hello"], np.zeros(shape=(1, 10)))

    def tearDown(self):
        self.saver.close()


if __name__ == "__main__":
    unittest.main()
