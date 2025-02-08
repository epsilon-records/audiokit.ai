"""Setup file for audiokit_ai package."""

from setuptools import find_packages, setup

setup(
    name="audiokit_ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "loguru",
        "python-osc",
        "sounddevice",
        "JACK-client",
        "mido",
        "openai",
        "soundfile",
    ],
    extras_require={
        "test": [
            "pytest",
            "pytest-mock",
            "pytest-cov",
        ],
    },
)
