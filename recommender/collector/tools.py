"""Tools for converting the collected data into useful models"""
from typing import Tuple, List, Dict
import librosa
import numpy as np


def mfcc(track: np.array, sr=25200, n_mfcc=32) -> np.ndarray:
    """
    Construct an MFCC to get a represention of the track.
    """
    return librosa.feature.spectral.mfcc(track, sr=sr, n_mfcc=n_mfcc)


def load_track_sample(file_name: str, sample_rate: int = 22050, duration: int = 30) -> (np.array, int):
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


def map_target(targets: List[str], mapping: Dict[str, int]) -> np.array:
    """
    Convert a list of strings to a sparse np.array based on a mapping
    Args:
        targets: the targets to map
        mapping: the mapping from the targets to the place in the array

    Returns:
        np.array: an array representing the targets as a sparse array to be used
            in the model
    """
    target = np.zeros((len(mapping)))

    for value in targets:
        target[mapping[value]] = 1

    return np.array(target)


def create_batch(data: List[Tuple[List[str], str]], mapping: List[str], consistent=True) -> (
        np.ndarray, np.ndarray):
    """
    Convert a list of tuples of lists of strings and a file string to both the input numpy array
    and the target numpy array.
    Args:
        data (List[Tuple[List[str], str]]): a list of tuples of lists of strings denoting the targets and a string
            denoting the filename. These should already be downloaded and ready to open.
            For example:
                [
                    (["happy", "optimistic", "jovial"], "merry.mp3")
                    (["sad", "unhappy", "pessimistic"], "gloomy.mp3")
                ]
        mapping (List[str]): a mapping of the targets to an index
        consistent: a boolean denoting whether the mapping should be sorted prior to mapping

    Returns:
        (np.ndarray, np.ndarray): a tuple with the first being the ndarray of tracks as mel-cepstrum spectrograms
            and the second being an ndarray of targets
    """
    mapping_ = {value: key
                for key, value in enumerate(sorted(mapping) if consistent else mapping)}
    track_spectrograms = []
    track_targets = []
    for targets, file in data:
        track_targets.append(map_target(targets, mapping_))
        t, sr = load_track_sample(file)
        track_spectrograms.append(mfcc(t, sr=sr))

    return np.vstack(track_spectrograms), np.vstack(track_targets)
