from setuptools import find_packages, setup


setup(
    name="audiokit",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
    ],
)
