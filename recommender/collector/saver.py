from typing import List, Dict
import fileinput
import numpy as np
import io
import logging
import os


class Saver:
    def save_results(self, tid: List[str], result: np.ndarray) -> None:
        pass

    def append_results(self, tid: List[str], result: np.ndarray):
        pass

    def condense_file(self):
        pass

    def close(self):
        pass


class FileSaver(Saver):
    def __init__(self, filename: str, logger: logging.Logger):
        self.__filename__ = filename
        self.__logger__ = logger
        dirname = os.path.dirname(filename)
        if not os.path.exists(filename):
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            self.__f__ = open(filename, "x+")
        else:
            self.__f__ = open(filename, "r+")

    def save_results(self, tid: List[str], result: np.ndarray) -> None:
        """
        Save a result to a file for storage. Highly inefficient.
        Args:
            tid (str): the id of the array
            result (np.ndarray): the array to be stored
        """
        m, _ = result.shape
        assert len(tid) == m
        self.__f__.seek(0, 0)

        arrays = np.split(result, len(tid))
        d = dict(zip(tid, result))

        lines = []

        for line in self.__f__:
            array = line.split(":")
            if len(array) != 2:
                self.__logger__.error(f"result file is improperly formatted: {line}")
                continue
            if array[0] in d:
                arrstr = np.array_str(d[array[0]], max_line_width=1000, precision=24, suppress_small=True)
                line = f"{array[0]}:{arrstr}\n"
            lines.append(line)
        self.__f__.close()
        os.remove(self.__filename__)
        self.__f__ = open(self.__filename__, "w+")
        self.__f__.seek(0, 0)
        for line in lines:
            self.__f__.write(line)
        self.__f__.seek(0, 0)

    def append_results(self, tid: List[str], result: np.ndarray):
        m, _ = result.shape
        assert len(tid) == m
        self.__f__.seek(0, io.SEEK_END)
        arrays = np.split(result, len(tid))
        for i in range(0, len(tid)):
            arrstr = np.array_str(arrays[i], max_line_width=1000, precision=24, suppress_small=True)
            self.__f__.write(f"{tid[i]}:{arrstr}\n")
        self.__f__.seek(0, 0)

    def condense_file(self):
        lines = {}
        self.__f__.seek(0, 0)
        for line in self.__f__:
            array = line.split(":")
            if len(array) != 2:
                self.__logger__.error(f"result file is improperly formatted: {line}")
                continue
            lines[array[0]] = array[1]
        self.__f__.close()
        os.remove(self.__filename__)
        self.__f__ = open(self.__filename__, "w+")
        self.__f__.seek(0, 0)
        for (key, value) in lines.items():
            self.__f__.write(f"{key}:{value}")

    def close(self):
        self.__f__.flush()
        self.__f__.close()
