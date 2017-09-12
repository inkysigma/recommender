"""Tools for converting the collected data into useful models"""
from typing import Tuple, List
from recommender.collector.music import Track
import librosa
import numpy as np


def mfcc(track: np.ndarray, n_mfcc=32) -> np.ndarray:
    """
    Construct an MFCC to get a represention of the track.
    """
    return librosa.feature.spectral.mfcc(track, n_mfcc=n_mfcc)


def load_track_sample(file_name: str, sample_rate: int = 22050, duration: int = 30) -> np.array:
    """
    Load a track based on a filename into a numpy array of signals.
    Use mfcc to convert the return value into a mel-cepstrum spectrogram.
    Args:
        file_name (str): the name of the file to load
        sample_rate (int): the sample rate of the track
        duration (int): the duration of the track in seconds

    Returns:
        np.array: the array of track signals loaded
    """
    return librosa.load(file_name, sr=sample_rate, duration=duration)


def create_targets(targets: List[str], mapping: List[str], consistent=True) -> np.array:
    """
    Convert a list of strings to a sparse np.array based on a mapping
    Args:
        targets: the targets to map
        mapping: the mapping from the targets to the place in the array
        consistent: whether or not to sort the mapping. Turn off if already sorted

    Returns:
        np.array: an array representing the targets as a sparse array to be used
            in the model
    """
    mapping_ = sorted(mapping) if consistent else mapping

def create_batch(data: List[Track, List[str]]):
    pass
