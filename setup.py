from setuptools import setup, find_packages

VERSION = '0.0.1'
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
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
