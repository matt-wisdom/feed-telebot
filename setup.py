#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = ["Matthew Wisdom"]
import codecs

import toml
from setuptools import find_packages, setup

pyproject = toml.load("pyproject.toml")


def long_description():
    """Read and return README as long description."""
    with codecs.open("README.md", encoding="utf-8-sig") as f:
        return f.read()


pyproject = toml.load("pyproject.toml")


def setup_package():
    """Set up package."""
    setup(
        author=pyproject["tool"]["poetry"]["authors"][0],
        description=pyproject["tool"]["poetry"]["description"],
        include_package_data=True,
        install_requires=pyproject["tool"]["poetry"]["dependencies"],
        keywords=[],
        license=pyproject["tool"]["poetry"]["license"],
        long_description=long_description(),
        name=pyproject["tool"]["poetry"]["name"],
        packages=find_packages(
            where=".",
            exclude=["tests", "tests.*"],
        ),
        url=pyproject["tool"]["poetry"]["repository"],
        setup_requires=pyproject["build-system"]["requires"],
        version=pyproject["tool"]["poetry"]["version"],
        zip_safe=True,
    )


if __name__ == "__main__":
    setup_package()
