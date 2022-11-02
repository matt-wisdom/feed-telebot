import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def set_test():
    os.environ["TESTING"] = "1"
