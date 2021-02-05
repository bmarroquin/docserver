from git import Repo


def get_repo_tags_without_download(repo: str):
    repo = Repo.clone_from(repo, "temp/repos", multi_options=["-n"])
    tags = list(repo.tags)
    repo.close()
    return tags
