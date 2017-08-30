"""Setup the recommender package. Requires tensorflow for training and predicting. Pyramid is used as an interface"""
from setuptools import setup

INSTALL_REQUIRES = [
    "tensorflow",
    "spotipy",
    "numpy",
    "pyramid"
]

setup(
    name="recommender",
    install_requires=INSTALL_REQUIRES
)
