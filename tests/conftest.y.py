import os
import shutil

import pytest


@pytest.fixture(scope="session")
def temp_directory():
    temp_dir = os.path.join(os.getcwd(), "temp")
    os.mkdir(temp_dir)
    yield temp_dir
    shutil.rmtree(temp_dir)
