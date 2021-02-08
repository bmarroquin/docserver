from typing import Optional

import semver
from git import Repo, TagReference, Head


def get_default_branch(repo: Repo):
    if repo.remotes:
        output = repo.git.execute(["git", "remote", "show", "origin"])
        # git remote show <remote> will include a line listing the default branch. Ex: HEAD branch: master
        # get he one line that starts with "HEAD branch"
        head_branch_line = [line for line in output.splitlines() if line.strip().startswith("HEAD branch")][0]
        default_branch = head_branch_line.split(":")[-1].strip()
    else:
        # for local repos during testing
        default_branch = repo.head.ref.name
    return default_branch


def _clean_version(version: str):
    return version.lstrip("vV")


def _get_additional_refs_to_build(repo: Repo, minimum_version: semver.VersionInfo):
    refs = []
    latest_version = None
    latest_ref = None
    for ref in repo.references:
        version_str = None

        if isinstance(ref, TagReference):
            # support for tags that meet [vV]?<version>
            version_str = _clean_version(ref.name)
        elif isinstance(ref, Head) and ref.name.lower().startswith("release/"):
            # support for release branches that meet [rR]elease/[vV]?<version>
            version_str = _clean_version(ref.name.split("/")[-1])

        if not version_str:
            # not a tag or release branch
            continue

        try:
            version = semver.VersionInfo.parse(version_str)
        except ValueError:
            # if the version cannot be parsed it does not meet supported version constraints
            continue

        if version < minimum_version:
            continue

        if not latest_version:
            latest_version = version
            latest_ref = ref
        elif version > latest_version:
            latest_version = version
            latest_ref = ref

        refs.append(ref)

    return refs, latest_ref


def get_refs_to_build(repo: Repo, minimum_version: Optional[semver.VersionInfo] = None):
    if not minimum_version:
        minimum_version = semver.VersionInfo.parse("0.0.0")

    default_branch = get_default_branch(repo)
    latest_ref = repo.heads[default_branch]
    refs_to_build, stable_ref = _get_additional_refs_to_build(repo, minimum_version)

    return latest_ref, stable_ref, refs_to_build
