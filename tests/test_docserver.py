from docserver.doc_import.git import get_repo_tags_without_download


def test_version():
    tags = get_repo_tags_without_download("https://github.com/bmarroquin/test_repo.git")
    assert tags == []
