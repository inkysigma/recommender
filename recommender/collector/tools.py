"""Tools for converting the collected data into useful models"""
import librosa
import numpy as np


def mfcc(track: np.ndarray, n_mfcc=32) -> np.ndarray:
    """
    Construct an MFCC to get a represention of the track.
    """
    return librosa.feature.spectral.mfcc(track, n_mfcc=n_mfcc)
