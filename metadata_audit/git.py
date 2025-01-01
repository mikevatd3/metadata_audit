"""
The Editions file records which commit was used to add the data to the 
table. The log_git function handles that and provides some reasonable errors
if that fails for some reason.

POTENTIAL ISSUES:
    - Doesn't deal with detatched head states

"""

from pathlib import Path
import pygit2
from pygit2 import GitError


class ScriptDirectoryError(Exception):
    """
    Raised if the upload script isn't placed at the root of the git repo.
    """


class ChangesNotCommittedError(Exception):
    """
    Raised if there are changes in the ETL script that have yet to be
    commited.
    """


def log_git(filepath: Path, lax=False):
    """
    log_git takes the file as an argument and returns a branch-commit key
    that can be logged in the metadata database to check if the upload is
    current. If the branch has not been committed, an
    """
    try:
        repo = pygit2.Repository(filepath.parent)  # type: ignore
    except GitError:
        raise ScriptDirectoryError("Script must live at root of git repo.")

    status_dict = repo.status()

    # If ANY file has a modified, deleted or otherwise changed status don't
    # continue to run the script.

    # I checked that these all are preset in the module--pygit2 has some
    # typing work to do...
    not_committed = any(
        flags
        & (
            pygit2.GIT_STATUS_WT_MODIFIED  # type: ignore
            | pygit2.GIT_STATUS_INDEX_MODIFIED  # type: ignore
            | pygit2.GIT_STATUS_INDEX_NEW  # type: ignore
            | pygit2.GIT_STATUS_INDEX_DELETED  # type: ignore
            | pygit2.GIT_STATUS_WT_DELETED  # type: ignore
            | pygit2.GIT_STATUS_WT_RENAMED  # type: ignore
            | pygit2.GIT_STATUS_INDEX_RENAMED  # type: ignore
            | pygit2.GIT_STATUS_INDEX_TYPECHANGE  # type: ignore
            | pygit2.GIT_STATUS_WT_TYPECHANGE  # type: ignore
        )
        for flags in status_dict.values()
    )

    if (not lax) and not_committed:
        raise ChangesNotCommittedError(
            "Commit changes before running the script to accurately capture "
            "intake script version."
        )

    short_commit_id = repo.head.peel(pygit2.Commit).short_id
    branch_name = repo.head.shorthand

    return f"{branch_name}-{short_commit_id}"
