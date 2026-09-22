import logging
import subprocess as sp
from dataclasses import dataclass
from os import chdir
from pathlib import Path


@dataclass
class Project:
    name: str
    url: str
    path: Path

    def __init__(self, name: str, url: str, path: Path) -> None:
        self.name = name
        self.url = url
        self.path = path.expanduser()


logger = logging.getLogger(__name__)


def pull_git_repositories(project: Project) -> Path:
    # Store the initial directory to safely return at the end
    original_dir = Path.cwd()
    base_path = project.path.parent

    class NotGitRepoError(Exception):
        pass

    class GitCloneError(Exception):
        pass

    class GitPullError(Exception):
        pass

    if not base_path.exists():
        logger.info(f"Directory '{base_path}' does not exist")
        base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory '{base_path}' created")

    logger.info(f"Checking directory: {project.path}")

    # Clone if the path does not exists
    if not project.path.exists():
        logger.error(
            f"Path '{project.path}' does not exist. Attempt to clone from '{project.url}'"
        )
        chdir(base_path)
        try:
            logger.info(f"Cloning from {project.url}")
            result = sp.run(
                ["git", "clone", project.url],
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info(f"Clone success:\n{result.stdout}")

        except sp.CalledProcessError as e:
            logger.error(f"'git clone' failed for '{project.url}'")
            raise GitCloneError(f"Error details:\n{e.stderr}")

        except Exception as e:
            logger.error(f"An unexpected error occurs: {e}")
            raise

    chdir(project.path)

    # Check if it is a valid git repository
    if not Path(".git").exists():
        logger.error(f"'{project.path}' is not a Git repo")
        raise NotGitRepoError(f"'{project.path}' is not a Git repo")

    try:
        logger.info(f"Pulling '{project.path}'")
        result = sp.run(
            ["git", "pull"],
            capture_output=True,
            text=True,
            check=True,
        )
        logger.info(f"Pull sueecss:\n{result.stdout}")

    except sp.CalledProcessError as e:
        logger.error(f"'git pull' failed for {project.path}")
        raise GitPullError(f"Error details:\n{e.stderr}")

    except Exception as e:
        logger.error(f"An unexpected error occurs: {e}")
        raise

    finally:
        # Always return to the original starting directory
        chdir(original_dir)

    return project.path
