import setuptools
from os import path

with open("README.md", "r") as fh:
    long_description = fh.read()

def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

setuptools.setup(
    name="pandiet",
    version="0.1.4",
    author="Makoto Yui",
    author_email="myui@apache.org",
    license = "BSD-3-Clause",
    license_file = "LICENSE",
    description="A library to reduce memory consumption of Pandas Dataframes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/myui/pandiet",
    project_urls={
        'Bug Tracker': 'https://github.com/myui/pandiet/issues',
        'Source': 'https://github.com/myui/pandiet/',
    },
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',

        # Specify the Python versions you support here.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    packages=setuptools.find_packages(),
    install_requires=parse_requirements('requirements.txt'),
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-cov"],
    python_requires=">=3.7,<4",
)