import os

import pytest
from git import Repo, rmtree


@pytest.fixture(scope="session")
def temp_directory():
    test_dir = os.path.join(os.getenv("TEMP"), "doc_server_tests")
    if os.path.isdir(test_dir):
        rmtree(test_dir)
    os.mkdir(test_dir)
    yield test_dir
    rmtree(test_dir)


@pytest.fixture
def sphinx_repo_url():
    return "https://github.com/bmarroquin/rtd_template.git"


@pytest.fixture
def sphinx_repo_local(temp_directory):
    return os.path.join(temp_directory, "sphinx_repo")


@pytest.fixture
def sphinx_repo(sphinx_repo_url, sphinx_repo_local):
    repo = Repo.clone_from(sphinx_repo_url, sphinx_repo_local)
    yield repo
    repo.close()
    rmtree(sphinx_repo_local)
