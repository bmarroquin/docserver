import os
import unittest

import pytest
import semver
from git import Repo, rmtree

from docserver.git_utils import get_refs_to_build


@pytest.fixture
def working_dir():
    return os.path.join(os.getcwd(), "repo")


@pytest.fixture
def version_file(working_dir):
    file_path = os.path.join(working_dir, "version.txt")
    return file_path


@pytest.fixture
def repo(working_dir, version_file) -> Repo:
    test_repo = Repo.init(working_dir)
    commit_file(test_repo, version_file, "InitialCommit", "initial commit")
    yield test_repo
    working_dir = test_repo.working_dir
    test_repo.close()
    rmtree(working_dir)


def commit_file(repo: Repo, file_path: str, value: str, commit_message: str):
    with open(file_path, "w") as file:
        file.write(value)
    repo.index.add(file_path)
    return repo.index.commit(commit_message)


def create_version(repo: Repo, file_path: str, version_type: str, version_value: str):
    commit = commit_file(repo, file_path, version_value, f"adds version {version_value}")
    if version_type == "tag":
        repo.create_tag(version_value, commit)
    else:
        repo.create_head(f"{version_type}/{version_value}")


def assert_count_equal(list1, list2):
    unittest.TestCase().assertCountEqual(list1, list2)


def test_get_refs_to_build_latest_no_remote(repo):
    # if there are no remotes it defaults to the current checked out head
    latest, stable, all_refs = get_refs_to_build(repo)
    assert latest.name == repo.head.ref.name


def test_get_refs_to_build_latest(sphinx_repo):
    latest, stable, all_refs = get_refs_to_build(sphinx_repo)
    assert latest.name == "master"


def test_get_refs_no_releases(repo):
    latest, stable, all_refs = get_refs_to_build(repo)
    assert stable is None
    assert_count_equal([ref.name for ref in all_refs], [])


def flatten_input_array(input_array):
    flattened = []
    for entry in input_array:
        if entry[1] == "invalid":
            continue
        elif entry[0] == "tag":
            flattened.append(entry[1])
        else:
            flattened.append(f"{entry[0]}/{entry[1]}")
    return flattened


versions = [
    ([("tag", "1.0.0")], "1.0.0"),
    ([("tag", "v1.0.0")], "v1.0.0"),
    ([("tag", "V1.0.0")], "V1.0.0"),
    ([("tag", "invalid")], None),
    ([("tag", "1.0.0"), ("tag", "invalid")], "1.0.0"),
    ([("tag", "1.0.0"), ("tag", "2.0.0")], "2.0.0"),
    ([("tag", "1.0.0"), ("tag", "1.0.1")], "1.0.1"),
    ([("tag", "v1.0.0"), ("tag", "2.0.0")], "2.0.0"),
    ([("tag", "V1.0.0"), ("tag", "2.0.0")], "2.0.0"),
    # release branches
    ([("release", "1.0.0")], "release/1.0.0"),
    ([("release", "v1.0.0")], "release/v1.0.0"),
    ([("release", "V1.0.0")], "release/V1.0.0"),
    ([("release", "invalid")], None),
    ([("release", "1.0.0"), ("release", "invalid")], "release/1.0.0"),
    ([("release", "1.0.0"), ("release", "2.0.0")], "release/2.0.0"),
    ([("release", "1.0.0"), ("release", "1.0.1")], "release/1.0.1"),
    ([("release", "v1.0.0"), ("release", "2.0.0")], "release/2.0.0"),
    ([("release", "V1.0.0"), ("release", "2.0.0")], "release/2.0.0"),
    # mixed mode
    ([("release", "V1.0.0"), ("tag", "2.0.0")], "2.0.0"),
    ([("tag", "v1.0.0"), ("release", "2.0.0")], "release/2.0.0"),
]


@pytest.mark.parametrize("test_input,expected_stable", versions)
def test_get_refs_stable_and_all(repo, version_file, test_input, expected_stable):
    for version in test_input:
        create_version(repo, version_file, version[0], version[1])

    latest, stable, all_refs = get_refs_to_build(repo)

    if expected_stable:
        assert stable.name == expected_stable
    else:
        assert stable is None

    expected_all = flatten_input_array(test_input)
    assert_count_equal([ref.name for ref in all_refs], expected_all)


def test_get_refs_all_with_minimum(repo, version_file):
    minimum_input = [
        ("tag", "1.0.0"),
        ("release", "1.1.0"),
        ("tag", "2.0.0"),
        ("release", "2.1.0"),
        ("tag", "v3.0.0"),
        ("release", "v3.1.0"),
        ("tag", "V4.0.0"),
        ("release", "V4.1.0"),
        ("tag", "invalid"),
        ("release", "invalid"),
    ]

    for version in minimum_input:
        create_version(repo, version_file, version[0], version[1])

    minimum_version = semver.VersionInfo.parse("1.0.0")
    maximum_version = semver.VersionInfo.parse("5.0.0")
    offset = 0
    expected_all = flatten_input_array(minimum_input)
    while minimum_version <= maximum_version:
        latest, stable, all_refs = get_refs_to_build(repo, minimum_version)
        if minimum_version.minor == 0:
            minimum_version = minimum_version.bump_minor()
        else:
            minimum_version = minimum_version.bump_major()

        expected = expected_all[offset:]

        if expected:
            # stable never changes because it is always the highest versions
            assert stable.name == "release/V4.1.0"
        else:
            # if nothing meets min stable will be None
            assert stable is None

        assert_count_equal([ref.name for ref in all_refs], expected)
        offset += 1
