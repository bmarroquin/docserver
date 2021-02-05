from git import Repo

from docserver.doc_import.git import get_repo_tags_without_download


def add_tag(repo: str, temp: str, tag: str):
    repo = Repo.clone_from(repo, temp)
    tag_ref = repo.create_tag("a")
    repo.remotes.origin.push(tag_ref)


def test_get_tags(testdir):
    tags = get_repo_tags_without_download("https://github.com/bmarroquin/test_repo.git")
    assert tags == []
    tags = get_repo_tags_without_download("https://github.com/bmarroquin/test_repo.git")
    assert tags == ["a"]
