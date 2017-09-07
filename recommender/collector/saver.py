import numpy as np


class Saver:
    def save_results(self, id: str, result: np.ndarray) -> None:
        pass


class HBaseSaver(Saver):
    def __init__(self):
        pass
