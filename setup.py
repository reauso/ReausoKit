from setuptools import setup, find_packages

VERSION = '0.0.0.0'
DESCRIPTION = 'Some util functionality for Python Projects.'

setup(
    name='ReausoKit',
    version=VERSION,
    description=DESCRIPTION,
    author='Rene Ebertowski',
    author_email='r.ebertowski@gmx.de',
    url='https://github.com/reauso/ReausoKit',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'parameterized',
    ],
)