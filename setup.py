# -*- coding: utf-8 -*-
"""
    Setup file for lexicons_builder.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 3.2.3.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
import sys

from pkg_resources import VersionConflict, require
from setuptools import setup, find_packages

# try:
#     require("setuptools>=38.3")
# except VersionConflict:
#     print("Error: version of setuptools is too old (<38.3)!")
#     sys.exit(1)


# if __name__ == "__main__":
#     setup(use_pyscaffold=True)


setup(
    name="lexicons_builder",
    # py_modules=["lexicons_builder"],
    entry_points={"console_scripts": ["lexicons_builder=lexicons_builder:main"]},
    version="0.1",
    description="lexicons_builder, a tool to create lexicons",
    author="Guillaume Le Noe-Bienvenu",
    author_email="glnb@gmail.com",
    url="https://gitlab.inria.fr/glenoebi/lexicons_builder",
    keywords=["lexicon", "nlp"],
    license="MIT",
    # packages = find_packages(exclude=("tests",))
    packages=find_packages(".."),
    # packages=['lexicons_builder'],
    # , 'scrappers', 'wordnet_explorer', 'nlp_model_explorer'],
    # install_requires=["feedparser", "html2text"],
    package_dir={
        "main_package": "lexicons_builder"
        # 'package1': '../Framework',
        #  'package2': '../Framework',
    },
)


# import pathlib
# from setuptools import setup

# # The directory containing this file
# HERE = pathlib.Path(__file__).parent

# # The text of the README file
# README = (HERE / "README.md").read_text()

# # This call to setup() does all the work
# setup(
#     name="realpython-reader",
#     version="1.0.0",
#     description="Read the latest Real Python tutorials",
#     long_description=README,
#     long_description_content_type="text/markdown",
#     url="https://github.com/realpython/reader",
#     author="Real Python",
#     author_email="info@realpython.com",
#     license="MIT",
#     classifiers=[
#         "License :: OSI Approved :: MIT License",
#         "Programming Language :: Python :: 3",
#         "Programming Language :: Python :: 3.7",
#     ],
#     include_package_data=True,
#     entry_points={
#         "console_scripts": [
#             "realpython=reader.__main__:main",
#         ]
#     },
# )
