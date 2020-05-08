"""Setup the project."""
from setuptools import setup, find_packages


setup(
    name='covid',
    version='0.1',
    packages=find_packages(),
    install_requires=['numpy>=1.18.3', 'pandas>=1.0.3', 'kaggle>=1.5.6', 'matplotlib>=3.2.1', 'jupyterlab>=1.1.0'],
    url='https://github.com/georgethebeatle/covid',
)
